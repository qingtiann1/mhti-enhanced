"""File scanning API routes.

异常处理：所有 FileSystemError 子类（FolderNotFoundError、InvalidFolderError、
PermissionDeniedError）由全局异常处理器统一处理，无需在 API 层手动捕获。
"""

from fastapi import APIRouter, Depends, Query

from server.core.auth import require_auth
from server.core.container import get_file_service, get_history_service
from server.models.file import BrowseResponse, ScanRequest, ScanResponse
from server.services.file_service import FileService
from server.services.fingerprint_service import calculate_fingerprint
from server.services.history_service import HistoryService

router = APIRouter(prefix="/api", tags=["files"], dependencies=[Depends(require_auth)])


@router.post("/scan", response_model=ScanResponse)
async def scan_folder(
    request: ScanRequest,
    file_service: FileService = Depends(get_file_service),
    history_service: HistoryService = Depends(get_history_service),
) -> ScanResponse:
    """
    Scan a folder for video files.

    Args:
        request: ScanRequest containing the folder path.
        file_service: Injected FileService instance.
        history_service: Injected HistoryService instance.

    Returns:
        ScanResponse with list of discovered video files.

    Raises:
        FolderNotFoundError: 文件夹不存在 (404)
        InvalidFolderError: 无效文件夹路径 (400)
        PermissionDeniedError: 权限被拒绝 (403)
    """
    files = file_service.scan_folder(request.folder_path)

    # 计算文件指纹并过滤已刮削的文件
    fingerprint_map = {}  # path -> fingerprint
    for f in files:
        fp = calculate_fingerprint(f.path)
        if fp:
            fingerprint_map[f.path] = fp

    # 查询已存在的指纹
    existing_fps = await history_service.get_existing_fingerprints(
        list(fingerprint_map.values())
    )

    # 过滤掉已刮削的文件
    filtered_files = [
        f for f in files
        if fingerprint_map.get(f.path) not in existing_fps
    ]

    return ScanResponse(
        folder_path=request.folder_path,
        total_files=len(filtered_files),
        files=filtered_files,
    )


@router.get("/files/browse", response_model=BrowseResponse)
async def browse_directory(
    path: str = Query(default="", description="Directory path to browse"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    file_service: FileService = Depends(get_file_service),
) -> BrowseResponse:
    """
    Browse a directory and list its contents.

    Args:
        path: Path to browse. Empty for root/drives.
        page: Page number (1-based).
        page_size: Number of items per page.
        file_service: Injected FileService instance.

    Returns:
        BrowseResponse with directory entries.

    Raises:
        FolderNotFoundError: 文件夹不存在 (404)
        InvalidFolderError: 无效文件夹路径 (400)
        PermissionDeniedError: 权限被拒绝 (403)
    """
    current_path, parent_path, entries, total = file_service.browse_directory(
        path, page, page_size
    )
    return BrowseResponse(
        current_path=current_path,
        parent_path=parent_path,
        entries=entries,
        total=total,
        page=page,
        page_size=page_size,
    )
