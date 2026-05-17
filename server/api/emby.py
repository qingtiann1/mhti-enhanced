"""Emby configuration API routes."""

from fastapi import APIRouter, Depends

from server.core.auth import require_auth
from server.core.container import get_emby_service
from server.models.emby import (
    ConflictCheckRequest,
    ConflictCheckResult,
    EmbyConfig,
    EmbyConfigRequest,
    EmbyConfigResponse,
    EmbyStatus,
    EmbyTestResponse,
)
from server.services.emby_service import EmbyService

router = APIRouter(prefix="/api/emby", tags=["emby"], dependencies=[Depends(require_auth)])


@router.get("/config", response_model=EmbyConfigResponse)
async def get_emby_config(
    service: EmbyService = Depends(get_emby_service),
) -> EmbyConfigResponse:
    """获取 Emby 配置"""
    config = await service.get_config()
    return EmbyConfigResponse(
        enabled=config.enabled,
        server_url=config.server_url,
        has_api_key=bool(config.api_key),
        user_id=config.user_id,
        library_ids=config.library_ids,
        check_before_scrape=config.check_before_scrape,
        timeout=config.timeout,
    )


@router.put("/config", response_model=EmbyConfigResponse)
async def save_emby_config(
    request: EmbyConfigRequest,
    service: EmbyService = Depends(get_emby_service),
) -> EmbyConfigResponse:
    """保存 Emby 配置"""
    # 如果没有提供新的 api_key，保留已保存的
    api_key = request.api_key
    if not api_key:
        saved_config = await service.get_config()
        api_key = saved_config.api_key

    config = EmbyConfig(
        enabled=request.enabled,
        server_url=request.server_url,
        api_key=api_key,
        user_id=request.user_id,
        library_ids=request.library_ids,
        check_before_scrape=request.check_before_scrape,
        timeout=request.timeout,
    )
    await service.save_config(config)
    return EmbyConfigResponse(
        enabled=config.enabled,
        server_url=config.server_url,
        has_api_key=bool(config.api_key),
        user_id=config.user_id,
        library_ids=config.library_ids,
        check_before_scrape=config.check_before_scrape,
        timeout=config.timeout,
    )


@router.get("/status", response_model=EmbyStatus)
async def get_emby_status(
    service: EmbyService = Depends(get_emby_service),
) -> EmbyStatus:
    """获取 Emby 连接状态"""
    return await service.get_status()


@router.post("/test", response_model=EmbyTestResponse)
async def test_emby_connection(
    request: EmbyConfigRequest | None = None,
    service: EmbyService = Depends(get_emby_service),
) -> EmbyTestResponse:
    """测试 Emby 连接，可传入配置或使用已保存的配置"""
    if request:
        # 如果 api_key 是特殊值，使用已保存的 api_key
        api_key = request.api_key
        if api_key == "__USE_SAVED__":
            saved_config = await service.get_config()
            api_key = saved_config.api_key

        config = EmbyConfig(
            enabled=True,
            server_url=request.server_url,
            api_key=api_key,
            user_id=request.user_id,
            library_ids=request.library_ids,
            check_before_scrape=request.check_before_scrape,
            timeout=request.timeout,
        )
        return await service.test_connection_with_config(config)
    return await service.test_connection()


@router.post("/check-conflict", response_model=ConflictCheckResult)
async def check_conflict(
    request: ConflictCheckRequest,
    service: EmbyService = Depends(get_emby_service),
) -> ConflictCheckResult:
    """检查 Emby 冲突"""
    return await service.check_conflict(request)
