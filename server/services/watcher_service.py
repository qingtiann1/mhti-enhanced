"""Folder watcher service for monitoring and auto-scraping."""

import asyncio
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Callable

import aiosqlite
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from server.core.database import DATABASE_PATH
from server.models.watcher import (
    DetectedFile,
    WatchedFolder,
    WatchedFolderCreate,
    WatchedFolderUpdate,
    WatcherMode,
    WatcherNotification,
    WatcherStatus,
    WatcherStatusResponse,
)

logger = logging.getLogger(__name__)

# Video file extensions to watch
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".wmv", ".mov", ".flv", ".ts", ".m2ts"}


class VideoFileHandler(FileSystemEventHandler):
    """处理视频文件事件的处理器"""

    def __init__(self, folder: WatchedFolder, callback: Callable[[str, WatchedFolder], None]):
        self.folder = folder
        self.callback = callback

    def _is_video_file(self, path: str) -> bool:
        """检查是否为视频文件"""
        ext = Path(path).suffix.lower()
        return ext in VIDEO_EXTENSIONS

    def on_created(self, event: FileCreatedEvent) -> None:
        """文件创建事件"""
        if event.is_directory:
            return
        if self._is_video_file(event.src_path):
            logger.info(f"检测到新文件: {event.src_path}")
            self.callback(event.src_path, self.folder)

    def on_moved(self, event: FileMovedEvent) -> None:
        """文件移动事件（重命名）"""
        if event.is_directory:
            return
        if self._is_video_file(event.dest_path):
            logger.info(f"检测到移动文件: {event.dest_path}")
            self.callback(event.dest_path, self.folder)


class WatchStrategy(ABC):
    """监控策略抽象基类"""

    def __init__(self, folder: WatchedFolder, on_file_detected: Callable[[str, WatchedFolder], None]):
        self.folder = folder
        self.on_file_detected = on_file_detected
        self._running = False

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass


class RealtimeStrategy(WatchStrategy):
    """实时监控策略 - 使用 watchdog"""

    def __init__(self, folder: WatchedFolder, on_file_detected: Callable[[str, WatchedFolder], None]):
        super().__init__(folder, on_file_detected)
        self._observer: Observer | None = None

    async def start(self) -> None:
        if self._running or not Path(self.folder.path).exists():
            return
        self._observer = Observer()
        handler = VideoFileHandler(self.folder, self.on_file_detected)
        self._observer.schedule(handler, self.folder.path, recursive=True)
        self._observer.start()
        self._running = True
        logger.info(f"[实时模式] 开始监控: {self.folder.path}")

    async def stop(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None
        self._running = False


class CompatStrategy(WatchStrategy):
    """兼容模式策略 - 定时轮询扫描"""

    def __init__(self, folder: WatchedFolder, on_file_detected: Callable[[str, WatchedFolder], None]):
        super().__init__(folder, on_file_detected)
        self._scan_task: asyncio.Task | None = None
        self._known_files: set[str] = set()

    async def start(self) -> None:
        if self._running or not Path(self.folder.path).exists():
            return
        self._running = True
        await self._init_known_files()
        self._scan_task = asyncio.create_task(self._scan_loop())
        logger.info(f"[兼容模式] 开始监控: {self.folder.path}")

    async def stop(self) -> None:
        self._running = False
        if self._scan_task:
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass
        self._known_files.clear()

    async def _init_known_files(self) -> None:
        for root, _, files in os.walk(self.folder.path):
            for f in files:
                if Path(f).suffix.lower() in VIDEO_EXTENSIONS:
                    self._known_files.add(str(Path(root) / f))

    async def _scan_loop(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(self.folder.scan_interval_seconds)
                if not self._running:
                    break
                current: set[str] = set()
                for root, _, files in os.walk(self.folder.path):
                    for f in files:
                        if Path(f).suffix.lower() in VIDEO_EXTENSIONS:
                            current.add(str(Path(root) / f))
                for fp in current - self._known_files:
                    self.on_file_detected(fp, self.folder)
                self._known_files = current
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[兼容模式] 扫描出错: {e}")


class WatcherService:
    """Service for folder watching and auto-scraping."""

    def __init__(self, db_path: Path | None = None):
        """Initialize watcher service."""
        self.db_path = db_path or DATABASE_PATH
        self._status = WatcherStatus.STOPPED
        self._running = False
        self._strategies: dict[str, WatchStrategy] = {}  # folder_id -> strategy
        self._pending_files: dict[str, tuple[str, float, WatchedFolder]] = {}  # path -> (path, detect_time, folder)
        self._last_detection: datetime | None = None
        self._on_files_detected: Callable[[WatcherNotification], None] | None = None
        self._process_task: asyncio.Task | None = None

    async def _ensure_db(self) -> None:
        """Ensure database directory exists and run migrations."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            # 兼容旧数据库：添加 mode 列
            cursor = await db.execute("PRAGMA table_info(watched_folders)")
            columns = [row[1] for row in await cursor.fetchall()]
            if "mode" not in columns:
                await db.execute("ALTER TABLE watched_folders ADD COLUMN mode TEXT DEFAULT 'realtime'")
            await db.commit()

    async def create_folder(self, folder: WatchedFolderCreate) -> WatchedFolder:
        """Create a new watched folder."""
        await self._ensure_db()

        folder_id = str(uuid.uuid4())[:8]
        now = datetime.now()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO watched_folders
                (id, path, enabled, mode, scan_interval_seconds, file_stable_seconds, auto_scrape, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    folder_id,
                    folder.path,
                    1 if folder.enabled else 0,
                    folder.mode.value,
                    folder.scan_interval_seconds,
                    folder.file_stable_seconds,
                    1 if folder.auto_scrape else 0,
                    now.isoformat(),
                ),
            )
            await db.commit()

        new_folder = WatchedFolder(
            id=folder_id,
            path=folder.path,
            enabled=folder.enabled,
            mode=folder.mode,
            scan_interval_seconds=folder.scan_interval_seconds,
            file_stable_seconds=folder.file_stable_seconds,
            auto_scrape=folder.auto_scrape,
            last_scan=None,
            created_at=now,
        )

        # 如果服务正在运行且文件夹启用，立即启动监控
        if self._running and folder.enabled:
            await self._start_folder_watch(new_folder)

        return new_folder

    async def list_folders(self) -> tuple[list[WatchedFolder], int]:
        """List all watched folders."""
        await self._ensure_db()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute("SELECT COUNT(*) as count FROM watched_folders")
            row = await cursor.fetchone()
            total = row["count"] if row else 0

            cursor = await db.execute(
                "SELECT * FROM watched_folders ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()

        folders = [self._row_to_folder(row) for row in rows]
        return folders, total

    async def get_folder(self, folder_id: str) -> WatchedFolder | None:
        """Get a watched folder by ID."""
        await self._ensure_db()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM watched_folders WHERE id = ?",
                (folder_id,),
            )
            row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_folder(row)

    async def update_folder(
        self, folder_id: str, update: WatchedFolderUpdate
    ) -> WatchedFolder | None:
        """Update a watched folder."""
        await self._ensure_db()

        folder = await self.get_folder(folder_id)
        if folder is None:
            return None

        updates = []
        values = []

        if update.path is not None:
            updates.append("path = ?")
            values.append(update.path)
        if update.enabled is not None:
            updates.append("enabled = ?")
            values.append(1 if update.enabled else 0)
        if update.mode is not None:
            updates.append("mode = ?")
            values.append(update.mode.value)
        if update.scan_interval_seconds is not None:
            updates.append("scan_interval_seconds = ?")
            values.append(update.scan_interval_seconds)
        if update.file_stable_seconds is not None:
            updates.append("file_stable_seconds = ?")
            values.append(update.file_stable_seconds)
        if update.auto_scrape is not None:
            updates.append("auto_scrape = ?")
            values.append(1 if update.auto_scrape else 0)

        if updates:
            values.append(folder_id)
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    f"UPDATE watched_folders SET {', '.join(updates)} WHERE id = ?",
                    values,
                )
                await db.commit()

        updated_folder = await self.get_folder(folder_id)

        # 如果服务正在运行，重启该文件夹的监控
        if self._running and updated_folder:
            await self._restart_folder_watch(updated_folder)

        return updated_folder

    async def delete_folder(self, folder_id: str) -> bool:
        """Delete a watched folder."""
        await self._ensure_db()

        # 先停止该文件夹的监控
        if folder_id in self._strategies:
            await self._stop_folder_watch(folder_id)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM watched_folders WHERE id = ?",
                (folder_id,),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_status(self) -> WatcherStatusResponse:
        """Get watcher status."""
        folders, _ = await self.list_folders()
        active = sum(1 for f in folders if f.enabled)

        return WatcherStatusResponse(
            status=self._status,
            active_watchers=len(self._strategies),
            last_detection=self._last_detection,
            pending_files=len(self._pending_files),
        )

    async def _start_folder_watch(self, folder: WatchedFolder) -> None:
        """启动单个文件夹的监控"""
        if folder.id in self._strategies:
            return
        strategy = RealtimeStrategy(folder, self._on_file_detected) if folder.mode == WatcherMode.REALTIME else CompatStrategy(folder, self._on_file_detected)
        await strategy.start()
        self._strategies[folder.id] = strategy

    async def _stop_folder_watch(self, folder_id: str) -> None:
        """停止单个文件夹的监控"""
        if folder_id in self._strategies:
            await self._strategies[folder_id].stop()
            del self._strategies[folder_id]

    async def _restart_folder_watch(self, folder: WatchedFolder) -> None:
        """重启单个文件夹的监控"""
        await self._stop_folder_watch(folder.id)
        if folder.enabled:
            await self._start_folder_watch(folder)

    async def start(
        self, on_files_detected: Callable[[WatcherNotification], None] | None = None
    ) -> None:
        """Start the watcher service."""
        if self._running:
            return

        self._on_files_detected = on_files_detected
        self._running = True
        self._status = WatcherStatus.RUNNING

        # 获取所有启用的监控文件夹
        folders, _ = await self.list_folders()
        enabled_folders = [f for f in folders if f.enabled]

        if not enabled_folders:
            logger.warning("没有启用的监控文件夹")

        # 为每个文件夹启动独立的监控策略
        for folder in enabled_folders:
            await self._start_folder_watch(folder)

        # 启动待处理文件检查任务
        self._process_task = asyncio.create_task(self._process_pending_files())

        # 在后台执行初始扫描
        asyncio.create_task(self._initial_scan(enabled_folders))

        logger.info(f"监控服务已启动，共 {len(self._strategies)} 个文件夹")

    async def _initial_scan(self, folders: list[WatchedFolder]) -> None:
        """启动时执行一次全量扫描，跳过已有待处理任务的文件"""
        from server.services.scrape_job_service import ScrapeJobService
        scrape_service = ScrapeJobService()
        pending_paths = await scrape_service.get_pending_file_paths()
        logger.info(f"已有 {len(pending_paths)} 个待处理任务，初始扫描将跳过这些文件")

        for folder in folders:
            folder_path = Path(folder.path)
            if not folder_path.exists():
                continue

            logger.info(f"扫描文件夹: {folder.path}")
            stable_files: list[DetectedFile] = []
            current_time = time.time()

            for root, _, files in os.walk(folder_path):
                for filename in files:
                    ext = Path(filename).suffix.lower()
                    if ext not in VIDEO_EXTENSIONS:
                        continue

                    filepath = Path(root) / filename
                    try:
                        stat = filepath.stat()
                        age = current_time - stat.st_mtime

                        if age >= folder.file_stable_seconds:
                            # 跳过已有待处理任务的文件
                            if str(filepath) in pending_paths:
                                continue
                            stable_files.append(
                                DetectedFile(
                                    path=str(filepath),
                                    detected_at=datetime.now(),
                                    file_size=stat.st_size,
                                    stable=True,
                                )
                            )
                        else:
                            self._pending_files[str(filepath)] = (str(filepath), current_time, folder)
                    except OSError:
                        continue

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE watched_folders SET last_scan = ? WHERE id = ?",
                    (datetime.now().isoformat(), folder.id),
                )
                await db.commit()

            if stable_files and folder.auto_scrape:
                logger.info(f"初始扫描发现 {len(stable_files)} 个稳定文件")
                await self._create_jobs_for_files(stable_files)

    def _on_file_detected(self, path: str, folder: WatchedFolder) -> None:
        """文件检测回调"""
        self._last_detection = datetime.now()
        self._pending_files[path] = (path, time.time(), folder)
        logger.info(f"文件加入待处理队列: {path}")

    async def _process_pending_files(self) -> None:
        """处理待处理文件的后台任务"""
        while self._running:
            try:
                await asyncio.sleep(5)

                if not self._pending_files:
                    continue

                current_time = time.time()
                stable_files: list[DetectedFile] = []
                to_remove: list[str] = []

                for path, (file_path, detect_time, folder) in list(self._pending_files.items()):
                    age = current_time - detect_time

                    if age >= folder.file_stable_seconds:
                        try:
                            stat = Path(file_path).stat()
                            file_age = current_time - stat.st_mtime

                            if file_age >= folder.file_stable_seconds:
                                stable_files.append(
                                    DetectedFile(
                                        path=file_path,
                                        detected_at=datetime.now(),
                                        file_size=stat.st_size,
                                        stable=True,
                                    )
                                )
                                to_remove.append(path)
                        except OSError:
                            to_remove.append(path)

                for path in to_remove:
                    self._pending_files.pop(path, None)

                # 创建任务
                if stable_files:
                    logger.info(f"处理 {len(stable_files)} 个稳定文件")
                    await self._create_jobs_for_files(stable_files)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"处理待处理文件时出错: {e}")

    async def stop(self) -> None:
        """Stop the watcher service."""
        self._running = False
        self._status = WatcherStatus.STOPPED

        # 停止所有文件夹的监控
        for folder_id in list(self._strategies.keys()):
            await self._stop_folder_watch(folder_id)

        if self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
            self._process_task = None

        logger.info("监控服务已停止")

    async def _create_jobs_for_files(self, files: list[DetectedFile]) -> None:
        """为检测到的文件创建刮削任务"""
        from server.services.scrape_job_service import ScrapeJobService
        from server.services.config_service import ConfigService
        from server.models.scrape_job import ScrapeJobCreate, ScrapeJobSource

        config_service = ConfigService()
        organize_config = await config_service.get_organize_config()

        organize_dir = organize_config.organize_dir
        metadata_dir = organize_config.metadata_dir
        link_mode = organize_config.organize_mode  # 读取整理模式配置

        if not organize_dir:
            logger.warning("未配置整理目录，跳过创建任务")
            return

        scrape_service = ScrapeJobService()

        for file in files:
            logger.info(f"为文件创建刮削任务: {file.path}")
            job_create = ScrapeJobCreate(
                file_path=file.path,
                output_dir=organize_dir,
                metadata_dir=metadata_dir,
                link_mode=link_mode,  # 传递整理模式
                source=ScrapeJobSource.WATCHER,
            )
            await scrape_service.create_job(job_create)

    def _row_to_folder(self, row) -> WatchedFolder:
        """Convert database row to WatchedFolder."""
        mode_value = row["mode"] if "mode" in row.keys() else "realtime"
        return WatchedFolder(
            id=row["id"],
            path=row["path"],
            enabled=bool(row["enabled"]),
            mode=WatcherMode(mode_value),
            scan_interval_seconds=row["scan_interval_seconds"],
            file_stable_seconds=row["file_stable_seconds"],
            auto_scrape=bool(row["auto_scrape"]),
            last_scan=datetime.fromisoformat(row["last_scan"]) if row["last_scan"] else None,
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        )
