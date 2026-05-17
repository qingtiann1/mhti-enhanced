"""Scraper service for orchestrating the scraping workflow.

该模块是刮削工作流的核心编排器，通过 Mixin 模式组织代码：
- ScraperConfigMixin: 配置管理
- ScraperMetadataMixin: 元数据处理（NFO、搜索结果）
- ScraperMediaMixin: 媒体文件处理（图片、字幕、Emby）
"""

import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

import httpx

from server.models.emby import ConflictType
from server.models.history import LogLevel, ScrapeLogEntry, ScrapeLogStep
from server.models.organize import OrganizeMode
from server.models.rename import RenameRequest
from server.models.scraper import (
    BatchScrapeRequest,
    BatchScrapeResponse,
    ScrapeByIdRequest,
    ScrapePreview,
    ScrapeRequest,
    ScrapeResult,
    ScrapeStatus,
)
from server.services.config_service import ConfigService
from server.services.bangumi_service import BangumiService
from server.services.emby_service import EmbyService
from server.services.hanime_service import HanimeService
from server.services.image_service import ImageService
from server.services.nfo_service import NFOService
from server.services.parser_service import ParserService
from server.services.rename_service import RenameService
from server.services.scraper_config import ScraperConfigMixin
from server.services.scraper_media import ScraperMediaMixin
from server.services.scraper_metadata import ScraperMetadataMixin
from server.services.subtitle_service import SubtitleService
from server.services.tmdb_service import TMDBService

from server.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

# 日志更新回调类型
LogUpdateCallback = Callable[[list[ScrapeLogStep]], Awaitable[None]]

# 整理模式中文名称映射
_MODE_NAMES = {
    OrganizeMode.COPY: "复制",
    OrganizeMode.MOVE: "移动",
    OrganizeMode.HARDLINK: "硬链接",
    OrganizeMode.SYMLINK: "软链接",
}


def _get_mode_name(mode: OrganizeMode | None) -> str:
    """获取整理模式的中文名称。"""
    if mode is None:
        return "移动"
    return _MODE_NAMES.get(mode, "移动")


class ScraperService(ScraperConfigMixin, ScraperMetadataMixin, ScraperMediaMixin):
    """Service for orchestrating the complete scraping workflow.

    通过 Mixin 模式组织代码，保持核心刮削逻辑清晰：
    - ScraperConfigMixin: 配置检查和获取
    - ScraperMetadataMixin: NFO 生成和搜索结果处理
    - ScraperMediaMixin: 图片下载、字幕处理、Emby 冲突检测
    """

    def __init__(
        self,
        config_service: ConfigService,
        tmdb_service: TMDBService,
        parser_service: ParserService,
        nfo_service: NFOService,
        rename_service: RenameService,
        image_service: ImageService,
        subtitle_service: SubtitleService,
        emby_service: EmbyService,
        hanime_service: HanimeService | None = None,
        bangumi_service: BangumiService | None = None,
        translation_service: TranslationService | None = None,
        bangumi_access_token: str = "",
        hanime_api_url: str = "",
    ) -> None:
        """Initialize scraper service with explicit dependencies.

        Args:
            config_service: Configuration service instance.
            tmdb_service: TMDB API service instance.
            parser_service: Filename parser service instance.
            nfo_service: NFO generation service instance.
            rename_service: File rename/move service instance.
            image_service: Image download service instance.
            subtitle_service: Subtitle handling service instance.
            emby_service: Emby integration service instance.
            bangumi_access_token: Bangumi API access token for R18 content.
            hanime_api_url: Base URL for hanime-server API.
        """
        self.config_service = config_service
        self.tmdb_service = tmdb_service
        self.parser_service = parser_service
        self.nfo_service = nfo_service
        self.rename_service = rename_service
        self.image_service = image_service
        self.subtitle_service = subtitle_service
        self.emby_service = emby_service
        self.hanime_service = hanime_service or HanimeService(base_url=hanime_api_url or None)
        self.bangumi_service = bangumi_service or BangumiService(access_token=bangumi_access_token)
        self.translation_service = translation_service or TranslationService()

    async def preview(self, file_path: str) -> ScrapePreview:
        """Preview scrape operation without executing.

        Args:
            file_path: Path to the video file.

        Returns:
            ScrapePreview with parsed info and search results.
        """
        path = Path(file_path)

        # Parse filename
        parsed = self.parser_service.parse(path.name, file_path)

        preview = ScrapePreview(
            file_path=file_path,
            parsed_title=parsed.series_name,
            parsed_season=parsed.season,
            parsed_episode=parsed.episode,
        )

        # Search TMDB if we have a title
        if parsed.series_name:
            try:
                search_response = await self.tmdb_service.search_series_by_api(parsed.series_name)
                preview.search_results = search_response.results
            except (httpx.TimeoutException, httpx.RequestError):
                pass

        return preview

    async def scrape_file(
        self,
        request: ScrapeRequest,
        on_log_update: LogUpdateCallback | None = None,
    ) -> ScrapeResult:
        """Execute complete scraping workflow for a single file.

        Workflow:
        1. Parse filename to extract series name, season, episode
        2. Search TMDB using API
        3. Auto-select best match (or return candidates)
        4. Get details via API
        5. Generate NFO
        6. Move file to organized location
        7. Download images
        8. Process subtitles

        Args:
            request: Scrape request with file path and options.
            on_log_update: Optional callback for real-time log updates.

        Returns:
            ScrapeResult with operation status and details.
        """
        file_path = request.file_path
        path = Path(file_path)
        scrape_logs: list[ScrapeLogStep] = []

        async def notify_log_update():
            """通知日志更新。"""
            if on_log_update:
                await on_log_update(scrape_logs)

        # Check file exists
        if not path.exists():
            return ScrapeResult(
                file_path=file_path,
                status=ScrapeStatus.MOVE_FAILED,
                message=f"文件不存在: {file_path}",
            )

        # Step 1: Parse filename
        parse_step = ScrapeLogStep(name="解析文件名", logs=[])
        parse_step.logs.append(ScrapeLogEntry(message=f"视频文件路径: {file_path}"))
        parsed = self.parser_service.parse(path.name, file_path)

        result = ScrapeResult(
            file_path=file_path,
            status=ScrapeStatus.SUCCESS,
            parsed_title=parsed.series_name,
            parsed_season=parsed.season,
            parsed_episode=parsed.episode,
        )

        if not parsed.series_name:
            parse_step.logs.append(ScrapeLogEntry(message="无法从文件名解析出剧集名称", level=LogLevel.ERROR))
            parse_step.completed = False
            scrape_logs.append(parse_step)
            await notify_log_update()
            result.status = ScrapeStatus.NO_MATCH
            result.message = "无法从文件名解析出剧集名称"
            result.scrape_logs = scrape_logs
            return result

        parse_step.logs.append(ScrapeLogEntry(message=f"解析结果: {parsed.series_name} S{parsed.season or '?'}E{parsed.episode or '?'}"))
        scrape_logs.append(parse_step)
        await notify_log_update()

        # Step 2: Search TMDB using API
        search_step = ScrapeLogStep(name="搜索 TMDB", logs=[])
        search_step.logs.append(ScrapeLogEntry(message=f"搜索关键词: {parsed.series_name}"))
        scrape_logs.append(search_step)
        await notify_log_update()

        try:
            search_response = await self.tmdb_service.search_series_by_api(parsed.series_name)
            # 只保留成人内容
            adult_results = [r for r in search_response.results if r.adult]
            result.search_results = adult_results
            search_step.logs.append(ScrapeLogEntry(message=f"找到 {len(adult_results)} 个匹配结果"))
            await notify_log_update()
        except httpx.TimeoutException:
            search_step.logs.append(ScrapeLogEntry(message="TMDB 搜索超时", level=LogLevel.ERROR))
            search_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.SEARCH_FAILED
            result.message = "TMDB 搜索超时，请检查网络或 Cookie"
            result.scrape_logs = scrape_logs
            return result
        except httpx.RequestError as e:
            search_step.logs.append(ScrapeLogEntry(message=f"TMDB 搜索失败: {str(e)}", level=LogLevel.ERROR))
            search_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.SEARCH_FAILED
            result.message = f"TMDB 搜索失败: {str(e)}"
            result.scrape_logs = scrape_logs
            return result

        if not adult_results:
            # Try hanime data source as fallback when TMDB finds nothing
            if parsed.video_id:
                search_step.logs.append(ScrapeLogEntry(message="TMDB 无匹配，尝试 Hanime 数据源..."))
                await notify_log_update()
                hanime_result = await self._scrape_via_hanime(
                    file_path, path, parsed, request, result, scrape_logs, on_log_update
                )
                if hanime_result:
                    return hanime_result

            # Try Bangumi as next fallback
            if parsed.series_name:
                search_step.logs.append(ScrapeLogEntry(message="尝试 Bangumi 数据源..."))
                await notify_log_update()
                bangumi_result = await self._scrape_via_bangumi(
                    file_path, path, parsed, request, result, scrape_logs, on_log_update
                )
                if bangumi_result:
                    return bangumi_result

            search_step.logs.append(ScrapeLogEntry(message="未找到匹配的成人剧集", level=LogLevel.WARNING))
            search_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.NO_MATCH
            result.message = f"未找到匹配的成人剧集: {parsed.series_name}"
            result.scrape_logs = scrape_logs
            return result

        # Step 3: Select match
        result.search_results = adult_results

        if request.auto_select and len(adult_results) == 1:
            # 只有一个结果时自动选择
            selected = adult_results[0]
            result.selected_id = selected.id
        elif request.auto_select and len(adult_results) > 1:
            # 多个结果时需要用户选择，先获取每个结果的详情
            search_step.logs.append(ScrapeLogEntry(message="获取各剧集详情..."))
            await notify_log_update()
            enriched_results = await self._enrich_search_results(adult_results)
            result.search_results = enriched_results
            result.status = ScrapeStatus.NEED_SELECTION
            result.message = f"找到 {len(adult_results)} 个匹配结果，请手动选择"
            result.scrape_logs = scrape_logs
            return result
        else:
            # Return results for manual selection
            search_step.logs.append(ScrapeLogEntry(message="获取各剧集详情..."))
            await notify_log_update()
            enriched_results = await self._enrich_search_results(adult_results)
            result.search_results = enriched_results
            result.status = ScrapeStatus.NEED_SELECTION
            result.message = "请手动选择匹配的剧集"
            result.scrape_logs = scrape_logs
            return result

        # Step 4: Get details via API
        detail_step = ScrapeLogStep(name="获取详情", logs=[])
        detail_step.logs.append(ScrapeLogEntry(message=f"获取剧集详情: TMDB ID {result.selected_id}"))
        scrape_logs.append(detail_step)
        await notify_log_update()

        try:
            series = await self.tmdb_service.get_series_by_api(result.selected_id)
            if series is None:
                detail_step.logs.append(ScrapeLogEntry(message="无法获取剧集详情", level=LogLevel.ERROR))
                detail_step.completed = False
                await notify_log_update()
                result.status = ScrapeStatus.API_FAILED
                result.message = f"无法获取剧集详情: ID {result.selected_id}"
                result.scrape_logs = scrape_logs
                return result
            result.series_info = series
            detail_step.logs.append(ScrapeLogEntry(message=f"剧集名称: {series.name}"))
            await notify_log_update()
        except ValueError as e:
            detail_step.logs.append(ScrapeLogEntry(message=str(e), level=LogLevel.ERROR))
            detail_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.API_FAILED
            result.message = str(e)
            result.scrape_logs = scrape_logs
            return result
        except httpx.TimeoutException:
            detail_step.logs.append(ScrapeLogEntry(message="TMDB API 请求超时", level=LogLevel.ERROR))
            detail_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.API_FAILED
            result.message = "TMDB API 请求超时"
            result.scrape_logs = scrape_logs
            return result
        except httpx.RequestError as e:
            detail_step.logs.append(ScrapeLogEntry(message=f"TMDB API 请求失败: {str(e)}", level=LogLevel.ERROR))
            detail_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.API_FAILED
            result.message = f"TMDB API 请求失败: {str(e)}"
            result.scrape_logs = scrape_logs
            return result

        # Step 4.5: Check if episode is missing
        if parsed.episode is None:
            # 如果剧集只有1集，自动选择
            total_episodes = series.number_of_episodes or 0
            if total_episodes == 1:
                parsed.episode = 1
                logger.info("剧集只有1集，自动选择 E01")
            else:
                # 多集需要手动选择，先获取季详情
                result.series_info = series
                season_num = parsed.season if parsed.season is not None else 1
                try:
                    season_detail = await self.tmdb_service.get_season_by_api(
                        result.selected_id, season_num
                    )
                    # 更新 series 中对应季的 episodes 信息
                    for i, s in enumerate(series.seasons):
                        if s.season_number == season_num:
                            series.seasons[i] = season_detail
                            break
                    result.series_info = series
                except Exception as e:
                    logger.warning(f"获取季度详情失败: {e}")

                result.status = ScrapeStatus.NEED_SEASON_EPISODE
                result.message = f"剧集共 {total_episodes} 集，请手动选择"
                result.scrape_logs = scrape_logs
                return result

        # Determine season and episode
        season_num = parsed.season if parsed.season is not None else 1
        episode_num = parsed.episode if parsed.episode is not None else 1

        # 记录程序选择的季/集
        select_step = ScrapeLogStep(name="确定季/集", logs=[])
        scrape_logs.append(select_step)
        if parsed.season is not None and parsed.episode is not None:
            select_step.logs.append(ScrapeLogEntry(message=f"从文件名解析: S{season_num:02d}E{episode_num:02d}"))
        else:
            msgs = []
            if parsed.season is None:
                msgs.append("季号默认为 1")
            if parsed.episode is None:
                msgs.append("集号默认为 1")
            select_step.logs.append(ScrapeLogEntry(message=f"程序自动选择: S{season_num:02d}E{episode_num:02d} ({', '.join(msgs)})"))
        await notify_log_update()

        # Step 5: Get season details (for episode info)
        season_info = None
        try:
            season_info = await self.tmdb_service.get_season_by_api(
                result.selected_id, season_num
            )
            logger.info(f"获取季度详情: Season {season_num}, 共 {len(season_info.episodes) if season_info and season_info.episodes else 0} 集")
        except Exception as e:
            logger.warning(f"获取季度详情失败: {e}")

        # Step 5.5: Emby 冲突检查
        emby_step = ScrapeLogStep(name="Emby 冲突检查", logs=[])
        scrape_logs.append(emby_step)
        try:
            conflict_result = await self._check_emby_conflict(
                series_name=series.name,
                tmdb_id=result.selected_id,
                season=season_num,
                episode=episode_num,
            )
        except Exception as e:
            logger.warning(f"Emby 冲突检查异常: {e}")
            from server.models.emby import ConflictCheckResult
            conflict_result = ConflictCheckResult(conflict_type=ConflictType.NO_CONFLICT)

        if conflict_result.conflict_type == ConflictType.EPISODE_EXISTS:
            emby_step.logs.append(ScrapeLogEntry(
                message=conflict_result.message or "Emby 中已存在该集",
                level=LogLevel.WARNING,
            ))
            emby_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.EMBY_CONFLICT
            result.message = conflict_result.message
            result.emby_conflict = conflict_result
            result.scrape_logs = scrape_logs
            return result
        elif conflict_result.conflict_type == ConflictType.SERIES_EXISTS:
            emby_step.logs.append(ScrapeLogEntry(
                message=conflict_result.message or "Emby 中已存在该剧集",
                level=LogLevel.SUCCESS,
            ))
        else:
            emby_step.logs.append(ScrapeLogEntry(message="无冲突"))
        await notify_log_update()

        # Step 6: Generate NFO
        nfo_step = ScrapeLogStep(name="生成 NFO", logs=[])
        scrape_logs.append(nfo_step)
        try:
            nfo_content = self._generate_episode_nfo(series, season_num, episode_num, season_info)
            nfo_step.logs.append(ScrapeLogEntry(message="NFO 内容生成成功"))
            await notify_log_update()
        except Exception as e:
            nfo_step.logs.append(ScrapeLogEntry(message=f"NFO 生成失败: {str(e)}", level=LogLevel.ERROR))
            nfo_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.NFO_FAILED
            result.message = f"NFO 生成失败: {str(e)}"
            result.scrape_logs = scrape_logs
            return result

        # Step 7: Move file using RenameService
        mode_name = _get_mode_name(request.link_mode)
        move_step = ScrapeLogStep(name=f"{mode_name}文件", logs=[])
        scrape_logs.append(move_step)
        try:
            year = series.first_air_date.year if series.first_air_date else None

            rename_request = RenameRequest(
                source_path=file_path,
                title=series.name,
                season=season_num,
                episode=episode_num,
                year=year,
                output_dir=request.output_dir,
                link_mode=request.link_mode,
            )

            move_step.logs.append(ScrapeLogEntry(message=f"源文件: {file_path}"))
            move_step.logs.append(ScrapeLogEntry(message=f"目标目录: {request.output_dir or '原目录'}"))
            move_step.logs.append(ScrapeLogEntry(message=f"整理模式: {mode_name}"))
            await notify_log_update()

            rename_result = self.rename_service.execute_rename(rename_request)

            if not rename_result.success:
                # 检查是否是文件冲突
                if rename_result.error and "already exists" in rename_result.error:
                    move_step.logs.append(ScrapeLogEntry(message=f"目标文件已存在: {rename_result.dest_path}", level=LogLevel.WARNING))
                    move_step.completed = False
                    await notify_log_update()
                    result.status = ScrapeStatus.FILE_CONFLICT
                    result.message = f"目标文件已存在: {rename_result.dest_path}"
                    result.dest_path = rename_result.dest_path
                    result.scrape_logs = scrape_logs
                    return result
                move_step.logs.append(ScrapeLogEntry(message=f"{mode_name}失败: {rename_result.error}", level=LogLevel.ERROR))
                move_step.completed = False
                await notify_log_update()
                result.status = ScrapeStatus.MOVE_FAILED
                result.message = rename_result.error
                result.scrape_logs = scrape_logs
                return result

            result.dest_path = rename_result.dest_path
            move_step.logs.append(ScrapeLogEntry(message=f"文件{mode_name}成功: {rename_result.dest_path}"))
            await notify_log_update()

            # 获取剧集文件夹路径（Season 文件夹的父目录）
            dest_file = Path(rename_result.dest_path)
            season_folder = dest_file.parent
            series_folder = season_folder.parent

            # 确定元数据输出目录（NFO、图片）
            if request.metadata_dir:
                # 使用独立的元数据目录，保持相同的目录结构
                metadata_base = Path(request.metadata_dir)
                metadata_series_folder = metadata_base / series_folder.name
                metadata_season_folder = metadata_series_folder / season_folder.name
                metadata_season_folder.mkdir(parents=True, exist_ok=True)
            else:
                # 元数据与视频同目录
                metadata_series_folder = series_folder
                metadata_season_folder = season_folder

            # Write episode NFO file (if enabled)
            nfo_config = await self._get_effective_nfo_config(request.advanced_settings)
            if nfo_config["nfo_enabled"]:
                nfo_path = metadata_season_folder / f"{dest_file.stem}.nfo"
                nfo_path.write_text(nfo_content, encoding="utf-8")
                result.nfo_path = str(nfo_path)
                move_step.logs.append(ScrapeLogEntry(message=f"NFO 文件已写入: {nfo_path}"))

                # 生成 tvshow.nfo（剧集信息）到剧集文件夹
                tvshow_nfo_path = metadata_series_folder / "tvshow.nfo"
                if not tvshow_nfo_path.exists():
                    metadata_series_folder.mkdir(parents=True, exist_ok=True)
                    tvshow_nfo_data = self.nfo_service.tvshow_from_tmdb(series)
                    tvshow_nfo_content = self.nfo_service.generate_tvshow_nfo(tvshow_nfo_data)
                    tvshow_nfo_path.write_text(tvshow_nfo_content, encoding="utf-8")
                    move_step.logs.append(ScrapeLogEntry(message="tvshow.nfo 已生成"))

                # 生成 season.nfo 到季度文件夹
                season_nfo_path = metadata_season_folder / "season.nfo"
                if not season_nfo_path.exists():
                    season_nfo_data = self._get_season_nfo_data(series, season_num)
                    season_nfo_content = self.nfo_service.generate_season_nfo(season_nfo_data)
                    season_nfo_path.write_text(season_nfo_content, encoding="utf-8")
                    move_step.logs.append(ScrapeLogEntry(message="season.nfo 已生成"))
            else:
                move_step.logs.append(ScrapeLogEntry(message="NFO 生成已跳过（配置禁用）"))

            await notify_log_update()

            # Step 8: Download images (based on config)
            image_step = ScrapeLogStep(name="下载图片", logs=[])
            scrape_logs.append(image_step)
            await notify_log_update()

            download_config = await self._get_effective_download_config(request.advanced_settings)

            # 下载剧集封面和背景图到元数据剧集文件夹
            if download_config["download_poster"] or download_config["download_fanart"]:
                await self._download_series_images(
                    series,
                    str(metadata_series_folder),
                    download_poster=download_config["download_poster"],
                    download_fanart=download_config["download_fanart"],
                )
                image_step.logs.append(ScrapeLogEntry(message="剧集图片处理完成"))
            else:
                image_step.logs.append(ScrapeLogEntry(message="剧集图片下载已跳过（配置禁用）"))
            await notify_log_update()

            # 下载集封面图到元数据季度文件夹
            if download_config["download_thumb"]:
                await self._download_episode_image(
                    season_info, season_num, episode_num, str(metadata_season_folder), dest_file.stem
                )
                image_step.logs.append(ScrapeLogEntry(message="集封面图处理完成"))
            else:
                image_step.logs.append(ScrapeLogEntry(message="集封面图下载已跳过（配置禁用）"))
            await notify_log_update()

            # 处理关联字幕文件
            self._process_subtitles(file_path, str(dest_file))

        except Exception as e:
            move_step.logs.append(ScrapeLogEntry(message=f"文件{mode_name}失败: {str(e)}", level=LogLevel.ERROR))
            move_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.MOVE_FAILED
            result.message = f"文件{mode_name}失败: {str(e)}"
            result.scrape_logs = scrape_logs
            return result

        # 设置集信息
        if season_info and season_info.episodes:
            for ep in season_info.episodes:
                if ep.episode_number == episode_num:
                    result.episode_info = ep
                    break

        # 更新实际使用的季/集号
        result.parsed_season = season_num
        result.parsed_episode = episode_num

        result.status = ScrapeStatus.SUCCESS
        result.message = "刮削完成"
        result.scrape_logs = scrape_logs
        await notify_log_update()
        return result

    async def scrape_by_id(
        self,
        request: ScrapeByIdRequest,
        on_log_update: LogUpdateCallback | None = None,
    ) -> ScrapeResult:
        """Scrape file with manually specified TMDB ID.

        Use this when automatic search fails.

        Args:
            request: Request with file path and TMDB ID.
            on_log_update: Optional callback for real-time log updates.

        Returns:
            ScrapeResult with operation status.
        """
        file_path = request.file_path
        path = Path(file_path)
        scrape_logs: list[ScrapeLogStep] = []

        async def notify_log_update():
            """通知日志更新。"""
            if on_log_update:
                await on_log_update(scrape_logs)

        if not path.exists():
            return ScrapeResult(
                file_path=file_path,
                status=ScrapeStatus.MOVE_FAILED,
                message=f"文件不存在: {file_path}",
            )

        result = ScrapeResult(
            file_path=file_path,
            status=ScrapeStatus.SUCCESS,
            selected_id=request.tmdb_id,
            parsed_season=request.season,
            parsed_episode=request.episode,
        )

        # Step 1: 获取剧集详情
        detail_step = ScrapeLogStep(name="获取详情", logs=[])
        detail_step.logs.append(ScrapeLogEntry(message=f"TMDB ID: {request.tmdb_id}, S{request.season:02d}E{request.episode:02d}"))
        scrape_logs.append(detail_step)
        await notify_log_update()

        try:
            series = await self.tmdb_service.get_series_by_api(request.tmdb_id)
            if series is None:
                detail_step.logs.append(ScrapeLogEntry(message="无法获取剧集详情", level=LogLevel.ERROR))
                detail_step.completed = False
                await notify_log_update()
                result.status = ScrapeStatus.API_FAILED
                result.message = f"无法获取剧集详情: ID {request.tmdb_id}"
                result.scrape_logs = scrape_logs
                return result
            result.series_info = series
            detail_step.logs.append(ScrapeLogEntry(message=f"剧集名称: {series.name}"))
            await notify_log_update()
        except ValueError as e:
            detail_step.logs.append(ScrapeLogEntry(message=str(e), level=LogLevel.ERROR))
            detail_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.API_FAILED
            result.message = str(e)
            result.scrape_logs = scrape_logs
            return result
        except (httpx.TimeoutException, httpx.RequestError) as e:
            detail_step.logs.append(ScrapeLogEntry(message=f"TMDB API 请求失败: {str(e)}", level=LogLevel.ERROR))
            detail_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.API_FAILED
            result.message = f"TMDB API 请求失败: {str(e)}"
            result.scrape_logs = scrape_logs
            return result

        # Get season details (for episode info)
        season_info = None
        try:
            season_info = await self.tmdb_service.get_season_by_api(
                request.tmdb_id, request.season
            )
            detail_step.logs.append(ScrapeLogEntry(message=f"获取季度详情: 共 {len(season_info.episodes) if season_info and season_info.episodes else 0} 集"))
            await notify_log_update()
        except Exception as e:
            logger.warning(f"获取季度详情失败: {e}")

        # Step 2: 生成 NFO
        nfo_step = ScrapeLogStep(name="生成 NFO", logs=[])
        scrape_logs.append(nfo_step)
        await notify_log_update()
        try:
            nfo_content = self._generate_episode_nfo(
                series, request.season, request.episode, season_info
            )
            nfo_step.logs.append(ScrapeLogEntry(message="NFO 内容生成成功"))
            await notify_log_update()
        except Exception as e:
            nfo_step.logs.append(ScrapeLogEntry(message=f"NFO 生成失败: {str(e)}", level=LogLevel.ERROR))
            nfo_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.NFO_FAILED
            result.message = f"NFO 生成失败: {str(e)}"
            result.scrape_logs = scrape_logs
            return result

        # Step 3: 移动文件
        mode_name = _get_mode_name(request.link_mode)
        move_step = ScrapeLogStep(name=f"{mode_name}文件", logs=[])
        scrape_logs.append(move_step)
        await notify_log_update()
        try:
            year = series.first_air_date.year if series.first_air_date else None

            rename_request = RenameRequest(
                source_path=file_path,
                title=series.name,
                season=request.season,
                episode=request.episode,
                year=year,
                output_dir=request.output_dir,
                link_mode=request.link_mode,
            )

            move_step.logs.append(ScrapeLogEntry(message=f"源文件: {path.name}"))
            move_step.logs.append(ScrapeLogEntry(message=f"目标目录: {request.output_dir or '原目录'}"))
            move_step.logs.append(ScrapeLogEntry(message=f"整理模式: {mode_name}"))
            await notify_log_update()

            rename_result = self.rename_service.execute_rename(rename_request)

            if not rename_result.success:
                move_step.logs.append(ScrapeLogEntry(message=f"{mode_name}失败: {rename_result.error}", level=LogLevel.ERROR))
                move_step.completed = False
                await notify_log_update()
                result.status = ScrapeStatus.MOVE_FAILED
                result.message = rename_result.error
                result.scrape_logs = scrape_logs
                return result

            result.dest_path = rename_result.dest_path
            move_step.logs.append(ScrapeLogEntry(message=f"文件{mode_name}成功: {rename_result.dest_path}"))
            await notify_log_update()

            # 获取剧集文件夹路径（Season 文件夹的父目录）
            dest_file = Path(rename_result.dest_path)
            season_folder = dest_file.parent
            series_folder = season_folder.parent

            # 确定元数据输出目录（NFO、图片）
            if request.metadata_dir:
                # 使用独立的元数据目录，保持相同的目录结构
                metadata_base = Path(request.metadata_dir)
                metadata_series_folder = metadata_base / series_folder.name
                metadata_season_folder = metadata_series_folder / season_folder.name
                metadata_season_folder.mkdir(parents=True, exist_ok=True)
            else:
                # 元数据与视频同目录
                metadata_series_folder = series_folder
                metadata_season_folder = season_folder

            # Write episode NFO (if enabled)
            nfo_config = await self._get_effective_nfo_config(request.advanced_settings)
            if nfo_config["nfo_enabled"]:
                nfo_path = metadata_season_folder / f"{dest_file.stem}.nfo"
                nfo_path.write_text(nfo_content, encoding="utf-8")
                result.nfo_path = str(nfo_path)
                move_step.logs.append(ScrapeLogEntry(message=f"NFO 文件已写入: {nfo_path}"))

                # 生成 tvshow.nfo（剧集信息）到剧集文件夹
                tvshow_nfo_path = metadata_series_folder / "tvshow.nfo"
                if not tvshow_nfo_path.exists():
                    metadata_series_folder.mkdir(parents=True, exist_ok=True)
                    tvshow_nfo_data = self.nfo_service.tvshow_from_tmdb(series)
                    tvshow_nfo_content = self.nfo_service.generate_tvshow_nfo(tvshow_nfo_data)
                    tvshow_nfo_path.write_text(tvshow_nfo_content, encoding="utf-8")
                    move_step.logs.append(ScrapeLogEntry(message="tvshow.nfo 已生成"))

                # 生成 season.nfo 到季度文件夹
                season_nfo_path = metadata_season_folder / "season.nfo"
                if not season_nfo_path.exists():
                    season_nfo_data = self._get_season_nfo_data(series, request.season)
                    season_nfo_content = self.nfo_service.generate_season_nfo(season_nfo_data)
                    season_nfo_path.write_text(season_nfo_content, encoding="utf-8")
                    move_step.logs.append(ScrapeLogEntry(message="season.nfo 已生成"))
            else:
                move_step.logs.append(ScrapeLogEntry(message="NFO 生成已跳过（配置禁用）"))

            await notify_log_update()

            # Step 4: 下载图片 (based on config)
            image_step = ScrapeLogStep(name="下载图片", logs=[])
            scrape_logs.append(image_step)
            await notify_log_update()

            download_config = await self._get_effective_download_config(request.advanced_settings)

            # 下载剧集封面和背景图到元数据剧集文件夹
            if download_config["download_poster"] or download_config["download_fanart"]:
                await self._download_series_images(
                    series,
                    str(metadata_series_folder),
                    download_poster=download_config["download_poster"],
                    download_fanart=download_config["download_fanart"],
                )
                image_step.logs.append(ScrapeLogEntry(message="剧集图片处理完成"))
            else:
                image_step.logs.append(ScrapeLogEntry(message="剧集图片下载已跳过（配置禁用）"))
            await notify_log_update()

            # 下载集封面图到元数据季度文件夹
            if download_config["download_thumb"]:
                await self._download_episode_image(
                    season_info, request.season, request.episode, str(metadata_season_folder), dest_file.stem
                )
                image_step.logs.append(ScrapeLogEntry(message="集封面图处理完成"))
            else:
                image_step.logs.append(ScrapeLogEntry(message="集封面图下载已跳过（配置禁用）"))
            await notify_log_update()

            # 处理关联字幕文件
            self._process_subtitles(file_path, str(dest_file))

        except Exception as e:
            move_step.logs.append(ScrapeLogEntry(message=f"文件{mode_name}失败: {str(e)}", level=LogLevel.ERROR))
            move_step.completed = False
            await notify_log_update()
            result.status = ScrapeStatus.MOVE_FAILED
            result.message = f"文件{mode_name}失败: {str(e)}"
            result.scrape_logs = scrape_logs
            return result

        # 设置集信息
        if season_info and season_info.episodes:
            for ep in season_info.episodes:
                if ep.episode_number == request.episode:
                    result.episode_info = ep
                    break

        result.status = ScrapeStatus.SUCCESS
        result.message = "刮削完成"
        result.scrape_logs = scrape_logs
        await notify_log_update()
        return result

    # ── Hanime NFO helpers ──────────────────────────────────────────

    def _generate_hanime_episode_nfo(
        self, detail, season_num: int, episode_num: int
    ) -> str:
        """Generate episode NFO XML from hanime video detail."""
        from server.models.nfo import EpisodeNFO
        title = detail.title or f"Episode {episode_num}"
        plot = detail.description or ""
        aired = None
        if detail.upload_date:
            try:
                from datetime import date
                aired = date.fromisoformat(detail.upload_date[:10])
            except (ValueError, IndexError):
                pass
        nfo_data = EpisodeNFO(
            title=title,
            season=season_num,
            episode=episode_num,
            plot=plot,
            aired=aired,
        )
        return self.nfo_service.generate_episode_nfo(nfo_data)

    def _generate_hanime_tvshow_nfo(self, detail) -> str:
        """Generate tvshow NFO XML from hanime video detail."""
        from server.models.nfo import TVShowNFO
        series_name = self.hanime_service.get_series_name(detail)
        year = self.hanime_service.get_year(detail)
        genres = self.hanime_service.get_genres(detail)
        plot = detail.description or ""
        aired = None
        if detail.upload_date:
            try:
                from datetime import date
                aired = date.fromisoformat(detail.upload_date[:10])
            except (ValueError, IndexError):
                pass
        nfo_data = TVShowNFO(
            title=series_name,
            original_title=detail.title,
            sort_title=series_name,
            plot=plot,
            genres=genres,
            year=year,
            premiered=aired,
        )
        return self.nfo_service.generate_tvshow_nfo(nfo_data)

    def _generate_hanime_season_nfo(self, detail, season_num: int) -> str:
        """Generate season NFO XML from hanime video detail."""
        from server.models.nfo import SeasonNFO
        aired = None
        if detail.upload_date:
            try:
                from datetime import date
                aired = date.fromisoformat(detail.upload_date[:10])
            except (ValueError, IndexError):
                pass
        nfo_data = SeasonNFO(
            season_number=season_num,
            title=f"Season {season_num}",
            premiered=aired,
        )
        return self.nfo_service.generate_season_nfo(nfo_data)

    async def _download_hanime_poster(self, cover_url: str, dest_dir: str) -> None:
        """Download poster image from hanime/Bangumi CDN."""
        import os
        dest_path = os.path.join(dest_dir, "poster.jpg")
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(cover_url)
            resp.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(resp.content)

    # ── End Hanime helpers ──────────────────────────────────────────

    async def _scrape_via_hanime(
        self,
        file_path: str,
        path: Path,
        parsed,
        request: ScrapeRequest,
        result: ScrapeResult,
        scrape_logs: list[ScrapeLogStep],
        on_log_update,
    ) -> ScrapeResult | None:
        """Try scraping via hanime-server API as a fallback data source.

        Returns ScrapeResult on success, None if hanime lookup fails.
        """
        video_id = parsed.video_id

        async def notify():
            if on_log_update:
                await on_log_update(scrape_logs)

        # Search hanime-server
        hanime_step = ScrapeLogStep(name="搜索 Hanime", logs=[])
        hanime_step.logs.append(ScrapeLogEntry(message=f"Hanime 视频 ID: {video_id}"))
        scrape_logs.append(hanime_step)
        await notify()

        detail = await self.hanime_service.get_video_detail(video_id)
        if detail is None:
            hanime_step.logs.append(ScrapeLogEntry(message="Hanime 数据源无匹配", level=LogLevel.WARNING))
            hanime_step.completed = False
            await notify()
            return None

        series_name = self.hanime_service.get_series_name(detail)
        episode_num = parsed.episode or self.hanime_service.get_episode_number(detail)
        season_num = parsed.season or 1

        hanime_step.logs.append(ScrapeLogEntry(message=f"Hanime 匹配: {series_name} S{season_num:02d}E{episode_num:02d}"))
        await notify()

        # Translate description to Chinese if needed
        if detail.description:
            detail.description = await self.translation_service.to_chinese(detail.description)

        # Generate NFO from hanime data
        nfo_step = ScrapeLogStep(name="生成 NFO (Hanime)", logs=[])
        scrape_logs.append(nfo_step)
        try:
            nfo_content = self._generate_hanime_episode_nfo(detail, season_num, episode_num)
            nfo_step.logs.append(ScrapeLogEntry(message="NFO 内容生成成功"))
        except Exception as e:
            nfo_step.logs.append(ScrapeLogEntry(message=f"NFO 生成失败: {e}", level=LogLevel.ERROR))
            nfo_step.completed = False
            await notify()
            result.status = ScrapeStatus.NFO_FAILED
            result.message = f"NFO 生成失败: {e}"
            result.scrape_logs = scrape_logs
            return result
        await notify()

        # Move file
        mode_name = _get_mode_name(request.link_mode)
        move_step = ScrapeLogStep(name=f"{mode_name}文件", logs=[])
        scrape_logs.append(move_step)
        try:
            year = self.hanime_service.get_year(detail)
            rename_request = RenameRequest(
                source_path=file_path,
                title=series_name,
                season=season_num,
                episode=episode_num,
                year=year,
                output_dir=request.output_dir,
                link_mode=request.link_mode,
            )
            move_step.logs.append(ScrapeLogEntry(message=f"源文件: {file_path}"))
            move_step.logs.append(ScrapeLogEntry(message=f"目标目录: {request.output_dir or '原目录'}"))
            await notify()

            rename_result = self.rename_service.execute_rename(rename_request)
            if not rename_result.success:
                if rename_result.error and "already exists" in rename_result.error:
                    result.status = ScrapeStatus.FILE_CONFLICT
                    result.message = f"目标文件已存在: {rename_result.dest_path}"
                    result.dest_path = rename_result.dest_path
                else:
                    result.status = ScrapeStatus.MOVE_FAILED
                    result.message = rename_result.error
                result.scrape_logs = scrape_logs
                return result

            result.dest_path = rename_result.dest_path
            move_step.logs.append(ScrapeLogEntry(message=f"文件{mode_name}成功: {rename_result.dest_path}"))
            await notify()

            dest_file = Path(rename_result.dest_path)
            season_folder = dest_file.parent
            series_folder = season_folder.parent

            if request.metadata_dir:
                metadata_base = Path(request.metadata_dir)
                metadata_series_folder = metadata_base / series_folder.name
                metadata_season_folder = metadata_series_folder / season_folder.name
                metadata_season_folder.mkdir(parents=True, exist_ok=True)
            else:
                metadata_series_folder = series_folder
                metadata_season_folder = season_folder

            # Write episode NFO
            nfo_config = await self._get_effective_nfo_config(request.advanced_settings)
            if nfo_config["nfo_enabled"]:
                nfo_path = metadata_season_folder / f"{dest_file.stem}.nfo"
                nfo_path.write_text(nfo_content, encoding="utf-8")
                result.nfo_path = str(nfo_path)
                move_step.logs.append(ScrapeLogEntry(message=f"NFO 已写入: {nfo_path}"))

                # Generate tvshow.nfo from hanime data
                tvshow_path = metadata_series_folder / "tvshow.nfo"
                if not tvshow_path.exists():
                    tvshow_nfo = self._generate_hanime_tvshow_nfo(detail)
                    metadata_series_folder.mkdir(parents=True, exist_ok=True)
                    tvshow_path.write_text(tvshow_nfo, encoding="utf-8")
                    move_step.logs.append(ScrapeLogEntry(message="tvshow.nfo 已生成"))

                # Generate season.nfo
                season_nfo_path = metadata_season_folder / "season.nfo"
                if not season_nfo_path.exists():
                    season_nfo = self._generate_hanime_season_nfo(detail, season_num)
                    season_nfo_path.write_text(season_nfo, encoding="utf-8")
                    move_step.logs.append(ScrapeLogEntry(message="season.nfo 已生成"))
            else:
                move_step.logs.append(ScrapeLogEntry(message="NFO 生成已跳过（配置禁用）"))
            await notify()

            # Download cover image from hanime CDN
            image_step = ScrapeLogStep(name="下载封面", logs=[])
            scrape_logs.append(image_step)
            download_config = await self._get_effective_download_config(request.advanced_settings)
            if download_config["download_poster"] and detail.cover_url:
                try:
                    await self._download_hanime_poster(detail.cover_url, str(metadata_series_folder))
                    image_step.logs.append(ScrapeLogEntry(message="封面图下载完成"))
                except Exception as e:
                    image_step.logs.append(ScrapeLogEntry(message=f"封面图下载失败: {e}", level=LogLevel.WARNING))
            await notify()

        except Exception as e:
            move_step.logs.append(ScrapeLogEntry(message=f"文件{mode_name}失败: {e}", level=LogLevel.ERROR))
            move_step.completed = False
            await notify()
            result.status = ScrapeStatus.MOVE_FAILED
            result.message = f"文件{mode_name}失败: {e}"
            result.scrape_logs = scrape_logs
            return result

        result.status = ScrapeStatus.SUCCESS
        result.message = "刮削完成 (Hanime)"
        result.scrape_logs = scrape_logs
        await notify()
        return result

    async def _scrape_via_bangumi(
        self,
        file_path: str,
        path: Path,
        parsed,
        request: ScrapeRequest,
        result: ScrapeResult,
        scrape_logs: list[ScrapeLogStep],
        on_log_update,
    ) -> ScrapeResult | None:
        """Try scraping via bgm.tv API as a fallback data source."""
        series_name = parsed.series_name

        async def notify():
            if on_log_update:
                await on_log_update(scrape_logs)

        bgm_step = ScrapeLogStep(name="搜索 Bangumi", logs=[])
        scrape_logs.append(bgm_step)

        # Use parsed series name (already cleaned by parser pipeline)
        clean_query = self.bangumi_service.clean_query(series_name)
        bgm_step.logs.append(ScrapeLogEntry(message=f"Bangumi 搜索: {clean_query}"))
        await notify()

        results = await self.bangumi_service.search_anime(clean_query)

        # Retry with fallback queries if no results OR match score too low
        best = self.bangumi_service.get_best_match(results, clean_query) if results else None

        if not best:
            fallback_queries = self._build_bangumi_fallback_queries(clean_query)
            for fbq in fallback_queries:
                if fbq == clean_query:
                    continue
                bgm_step.logs.append(ScrapeLogEntry(message=f"Bangumi 重试: {fbq}"))
                await notify()
                fb_results = await self.bangumi_service.search_anime(fbq)
                if fb_results:
                    fb_best = self.bangumi_service.get_best_match(fb_results, fbq)
                    if fb_best:
                        results = fb_results
                        best = fb_best
                        clean_query = fbq
                        break

        if not results:
            bgm_step.logs.append(ScrapeLogEntry(message="Bangumi 无搜索结果", level=LogLevel.WARNING))
            bgm_step.completed = False
            await notify()
            return None

        if best is None:
            bgm_step.logs.append(ScrapeLogEntry(message="Bangumi 匹配度过低", level=LogLevel.WARNING))
            bgm_step.completed = False
            await notify()
            return None

        bgm_title = self.bangumi_service.get_title(best)
        bgm_step.logs.append(ScrapeLogEntry(message=f"Bangumi 匹配: [{best.id}] {bgm_title}"))
        await notify()

        # Fetch full subject details from v0 API for summary (search API never returns summary)
        detail = await self.bangumi_service.get_subject_detail(best.id)
        if detail:
            best = self.bangumi_service.enrich_search_result(best, detail)
            if best.summary:
                bgm_step.logs.append(ScrapeLogEntry(message="已获取 Bangumi 摘要"))
            else:
                bgm_step.logs.append(ScrapeLogEntry(message="Bangumi 摘要为空", level=LogLevel.WARNING))
        else:
            bgm_step.logs.append(ScrapeLogEntry(message="无法获取 Bangumi 详情 (可能需要授权)", level=LogLevel.WARNING))

        # Translate summary to Chinese if needed
        if best.summary:
            best.summary = await self.translation_service.to_chinese(best.summary)

        episode_num = parsed.episode or 1
        season_num = parsed.season or 1

        # Generate NFO from Bangumi data
        nfo_step = ScrapeLogStep(name="生成 NFO (Bangumi)", logs=[])
        scrape_logs.append(nfo_step)
        try:
            nfo_content = self._generate_bangumi_episode_nfo(best, season_num, episode_num)
            nfo_step.logs.append(ScrapeLogEntry(message="NFO 内容生成成功"))
        except Exception as e:
            nfo_step.logs.append(ScrapeLogEntry(message=f"NFO 生成失败: {e}", level=LogLevel.ERROR))
            nfo_step.completed = False
            await notify()
            result.status = ScrapeStatus.NFO_FAILED
            result.message = f"NFO 生成失败: {e}"
            result.scrape_logs = scrape_logs
            return result
        await notify()

        # Move/copy file
        mode_name = _get_mode_name(request.link_mode)
        move_step = ScrapeLogStep(name=f"{mode_name}文件", logs=[])
        scrape_logs.append(move_step)
        try:
            year = self.bangumi_service.get_year(best)
            rename_request = RenameRequest(
                source_path=file_path,
                title=bgm_title,
                season=season_num,
                episode=episode_num,
                year=year,
                output_dir=request.output_dir,
                link_mode=request.link_mode,
            )
            move_step.logs.append(ScrapeLogEntry(message=f"源文件: {file_path}"))
            move_step.logs.append(ScrapeLogEntry(message=f"目标目录: {request.output_dir or '原目录'}"))
            await notify()

            rename_result = self.rename_service.execute_rename(rename_request)
            if not rename_result.success:
                if rename_result.error and "already exists" in rename_result.error:
                    result.status = ScrapeStatus.FILE_CONFLICT
                    result.message = f"目标文件已存在: {rename_result.dest_path}"
                    result.dest_path = rename_result.dest_path
                else:
                    result.status = ScrapeStatus.MOVE_FAILED
                    result.message = rename_result.error
                result.scrape_logs = scrape_logs
                return result

            result.dest_path = rename_result.dest_path
            move_step.logs.append(ScrapeLogEntry(message=f"文件{mode_name}成功: {rename_result.dest_path}"))
            await notify()

            dest_file = Path(rename_result.dest_path)
            season_folder = dest_file.parent
            series_folder = season_folder.parent

            if request.metadata_dir:
                metadata_base = Path(request.metadata_dir)
                metadata_series_folder = metadata_base / series_folder.name
                metadata_season_folder = metadata_series_folder / season_folder.name
                metadata_season_folder.mkdir(parents=True, exist_ok=True)
            else:
                metadata_series_folder = series_folder
                metadata_season_folder = season_folder

            # Write episode NFO
            nfo_config = await self._get_effective_nfo_config(request.advanced_settings)
            if nfo_config["nfo_enabled"]:
                nfo_path = metadata_season_folder / f"{dest_file.stem}.nfo"
                nfo_path.write_text(nfo_content, encoding="utf-8")
                result.nfo_path = str(nfo_path)
                move_step.logs.append(ScrapeLogEntry(message=f"NFO 已写入: {nfo_path}"))

                # tvshow.nfo
                tvshow_path = metadata_series_folder / "tvshow.nfo"
                if not tvshow_path.exists():
                    tvshow_nfo = self._generate_bangumi_tvshow_nfo(best)
                    metadata_series_folder.mkdir(parents=True, exist_ok=True)
                    tvshow_path.write_text(tvshow_nfo, encoding="utf-8")
                    move_step.logs.append(ScrapeLogEntry(message="tvshow.nfo 已生成"))

                # season.nfo
                season_nfo_path = metadata_season_folder / "season.nfo"
                if not season_nfo_path.exists():
                    season_nfo = self._generate_bangumi_season_nfo(best, season_num)
                    season_nfo_path.write_text(season_nfo, encoding="utf-8")
                    move_step.logs.append(ScrapeLogEntry(message="season.nfo 已生成"))
            await notify()

            # Download cover
            image_step = ScrapeLogStep(name="下载封面", logs=[])
            scrape_logs.append(image_step)
            download_config = await self._get_effective_download_config(request.advanced_settings)
            cover_url = self.bangumi_service.get_cover_url(best)
            if download_config["download_poster"] and cover_url:
                try:
                    await self._download_hanime_poster(cover_url, str(metadata_series_folder))
                    image_step.logs.append(ScrapeLogEntry(message="封面图下载完成"))
                except Exception as e:
                    image_step.logs.append(ScrapeLogEntry(message=f"封面图下载失败: {e}", level=LogLevel.WARNING))
            await notify()

        except Exception as e:
            move_step.logs.append(ScrapeLogEntry(message=f"文件{mode_name}失败: {e}", level=LogLevel.ERROR))
            move_step.completed = False
            await notify()
            result.status = ScrapeStatus.MOVE_FAILED
            result.message = f"文件{mode_name}失败: {e}"
            result.scrape_logs = scrape_logs
            return result

        result.status = ScrapeStatus.SUCCESS
        result.message = "刮削完成 (Bangumi)"
        result.scrape_logs = scrape_logs
        await notify()
        return result

    # ── Bangumi NFO helpers ──────────────────────────────────────────

    def _generate_bangumi_episode_nfo(self, result, season_num: int, episode_num: int) -> str:
        """Generate episode NFO from Bangumi search result."""
        from server.models.nfo import EpisodeNFO
        title = self.bangumi_service.get_title(result)
        plot = result.summary or ""
        aired = None
        if result.air_date:
            try:
                from datetime import date
                aired = date.fromisoformat(result.air_date)
            except (ValueError, IndexError):
                pass
        nfo_data = EpisodeNFO(
            title=f"{title} E{episode_num:02d}",
            season=season_num,
            episode=episode_num,
            plot=plot,
            aired=aired,
        )
        return self.nfo_service.generate_episode_nfo(nfo_data)

    def _generate_bangumi_tvshow_nfo(self, result) -> str:
        """Generate tvshow NFO from Bangumi search result."""
        from server.models.nfo import TVShowNFO
        title = self.bangumi_service.get_title(result)
        original = self.bangumi_service.get_original_title(result)
        year = self.bangumi_service.get_year(result)
        aired = None
        if result.air_date:
            try:
                from datetime import date
                aired = date.fromisoformat(result.air_date)
            except (ValueError, IndexError):
                pass
        nfo_data = TVShowNFO(
            title=title,
            original_title=original or None,
            sort_title=title,
            plot=result.summary or "",
            year=year,
            premiered=aired,
        )
        return self.nfo_service.generate_tvshow_nfo(nfo_data)

    def _generate_bangumi_season_nfo(self, result, season_num: int) -> str:
        """Generate season NFO from Bangumi search result."""
        from server.models.nfo import SeasonNFO
        aired = None
        if result.air_date:
            try:
                from datetime import date
                aired = date.fromisoformat(result.air_date)
            except (ValueError, IndexError):
                pass
        nfo_data = SeasonNFO(
            season_number=season_num,
            title=f"Season {season_num}",
            premiered=aired,
        )
        return self.nfo_service.generate_season_nfo(nfo_data)

    def _build_bangumi_fallback_queries(self, query: str) -> list[str]:
        """Build fallback search queries when the primary query fails.

        Generates progressively simpler queries to improve match chances.
        Tries Japanese-only names when Chinese-mixed queries don't match.
        """
        import re
        queries = [query]

        # Strip trailing standalone numbers (likely episode numbers)
        no_num = re.sub(r"\s+\d{1,2}\s*$", "", query).strip()
        if no_num and no_num != query:
            queries.append(no_num)

        # Strip leading numbers
        no_lead = re.sub(r"^\d{1,2}\s+", "", query).strip()
        if no_lead and no_lead not in queries:
            queries.append(no_lead)

        # Japanese-only (katakana + hiragana + kanji, but try kana-only first)
        kana = re.findall(r"[ァ-ヴー]+", query)
        if kana:
            kana_query = " ".join(kana).strip()
            if kana_query and kana_query not in queries and len(kana_query) >= 3:
                queries.append(kana_query)

        # CJK+混合 (all Japanese scripts + Chinese characters)
        cjk = re.findall(r"[぀-ゟ゠-ヿ一-鿿㐀-䶿]+", query)
        if cjk and len(cjk) >= 1:
            cjk_query = " ".join(cjk).strip()
            if cjk_query and cjk_query not in queries and len(cjk_query) >= 3:
                queries.append(cjk_query)

        # Latin-only extraction (for titles with both CJK and Latin)
        latin = re.findall(r"[a-zA-Z!?]+(?:\s+[a-zA-Z!?]+)*", query)
        if latin:
            latin_query = max(latin, key=len).strip()
            if latin_query and latin_query not in queries and len(latin_query) >= 3:
                queries.append(latin_query)

        # Deduplicate while preserving order
        seen = set()
        result = []
        for q in queries:
            if q and q not in seen:
                seen.add(q)
                result.append(q)
        return result

    # ── End Bangumi helpers ──────────────────────────────────────────

    async def batch_scrape(self, request: BatchScrapeRequest) -> BatchScrapeResponse:
        """Batch scrape multiple files.

        Args:
            request: Batch request with file paths.

        Returns:
            BatchScrapeResponse with all results.
        """
        results: list[ScrapeResult] = []

        for file_path in request.file_paths:
            if request.dry_run:
                # Preview only
                preview = await self.preview(file_path)
                results.append(
                    ScrapeResult(
                        file_path=file_path,
                        status=ScrapeStatus.SUCCESS,
                        parsed_title=preview.parsed_title,
                        parsed_season=preview.parsed_season,
                        parsed_episode=preview.parsed_episode,
                        search_results=preview.search_results,
                    )
                )
            else:
                scrape_request = ScrapeRequest(
                    file_path=file_path,
                    output_dir=request.output_dir,
                    auto_select=request.auto_select,
                )
                result = await self.scrape_file(scrape_request)
                results.append(result)

        success_count = sum(1 for r in results if r.status == ScrapeStatus.SUCCESS)
        failed_count = len(results) - success_count

        return BatchScrapeResponse(
            total=len(results),
            success=success_count,
            failed=failed_count,
            results=results,
        )
