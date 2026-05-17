"""Folder watcher data models."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class WatcherMode(str, Enum):
    """监控模式枚举"""

    REALTIME = "realtime"  # 实时模式：监听文件系统事件
    COMPAT = "compat"  # 兼容模式：定时轮询


class WatcherConfig(BaseModel):
    """监控全局配置模型"""

    enabled: bool = False  # 启用目录监控
    mode: WatcherMode = WatcherMode.REALTIME  # 监控模式
    performance_mode: bool = False  # 性能模式
    watch_dirs: list[str] = []  # 监控目录列表


class WatcherConfigRequest(BaseModel):
    """监控配置请求模型"""

    enabled: bool = False
    mode: WatcherMode = WatcherMode.REALTIME
    performance_mode: bool = False
    watch_dirs: list[str] = []


class WatcherConfigResponse(BaseModel):
    """监控配置响应模型"""

    enabled: bool
    mode: WatcherMode
    performance_mode: bool
    watch_dirs: list[str]


class WatcherStatus(str, Enum):
    """Watcher status enum."""

    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class WatchedFolder(BaseModel):
    """Watched folder model."""

    id: str
    path: str
    enabled: bool = True
    mode: WatcherMode = WatcherMode.REALTIME  # 每个文件夹独立监控模式
    scan_interval_seconds: int = 60
    file_stable_seconds: int = 30
    auto_scrape: bool = True
    last_scan: datetime | None = None
    created_at: datetime | None = None


class WatchedFolderCreate(BaseModel):
    """Request model for creating a watched folder."""

    path: str
    enabled: bool = True
    mode: WatcherMode = WatcherMode.REALTIME
    scan_interval_seconds: int = 60
    file_stable_seconds: int = 30
    auto_scrape: bool = True


class WatchedFolderUpdate(BaseModel):
    """Request model for updating a watched folder."""

    path: str | None = None
    enabled: bool | None = None
    mode: WatcherMode | None = None
    scan_interval_seconds: int | None = None
    file_stable_seconds: int | None = None
    auto_scrape: bool | None = None


class WatchedFolderResponse(BaseModel):
    """Response model for watched folder."""

    id: str
    path: str
    enabled: bool
    mode: WatcherMode
    scan_interval_seconds: int
    file_stable_seconds: int
    auto_scrape: bool
    last_scan: datetime | None
    created_at: datetime | None


class WatchedFolderListResponse(BaseModel):
    """Response model for watched folder list."""

    folders: list[WatchedFolder]
    total: int


class WatcherStatusResponse(BaseModel):
    """Response model for watcher status."""

    status: WatcherStatus
    active_watchers: int
    last_detection: datetime | None = None
    pending_files: int = 0


class DetectedFile(BaseModel):
    """Detected file model."""

    path: str
    detected_at: datetime
    file_size: int
    stable: bool = False


class WatcherNotification(BaseModel):
    """Notification for detected files."""

    folder_id: str
    folder_path: str
    files: list[DetectedFile]
    message: str
