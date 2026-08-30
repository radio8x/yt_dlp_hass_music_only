"""YouTube-DLP integration for Home Assistant.

Bản tùy biến: chỉ giữ lại service `yt_dlp.play` để phát một link YouTube/HTTP(S)
qua một media_player. Toàn bộ tải xuống, playlist đa loa, quét thư viện, DLNA,
TV, favorites và thẻ giao diện Lovelace đã bị loại bỏ khỏi mã nguồn.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_FILE_PATH
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.typing import ConfigType

from .const import CONF_MEDIA_LIBRARY_PATH, DOMAIN, STATE_DOWNLOADER
from .helpers import normalize_download_directory
from .manager import YoutubeDlpManager
from .media_http import YoutubeDlpMediaView, YoutubeDlpStreamView
from .play_services import async_register_play_services
from .playback import PlaybackManager

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_DATA_MEDIA_VIEW = f"{DOMAIN}_media_view_registered"
_DATA_STREAM_VIEW = f"{DOMAIN}_stream_view_registered"
_DATA_CORE_SERVICES = f"{DOMAIN}_core_services_registered"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the HTTP stream endpoints and the `play` service."""
    if not hass.data.get(_DATA_MEDIA_VIEW):
        hass.http.register_view(YoutubeDlpMediaView())
        hass.data[_DATA_MEDIA_VIEW] = True
    if not hass.data.get(_DATA_STREAM_VIEW):
        hass.http.register_view(YoutubeDlpStreamView())
        hass.data[_DATA_STREAM_VIEW] = True

    if not hass.data.get(_DATA_CORE_SERVICES):
        async_register_play_services(hass)
        hass.data[_DATA_CORE_SERVICES] = True

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Publish the core runtime without blocking Home Assistant startup."""
    download_path = normalize_download_directory(str(entry.data.get(CONF_FILE_PATH) or ""))
    library_path = normalize_download_directory(
        str(entry.data.get(CONF_MEDIA_LIBRARY_PATH) or download_path)
    )

    manager = YoutubeDlpManager(hass, entry, download_path, None)
    manager.playback_manager = PlaybackManager(hass, entry, library_path)
    entry.runtime_data = manager
    manager.async_publish_state()

    @callback
    def _schedule_post_start(_hass: HomeAssistant) -> None:
        entry.async_create_background_task(
            hass,
            _async_start_optional_runtime(hass, entry, manager),
            "yt_dlp_post_start",
        )

    entry.async_on_unload(async_at_started(hass, _schedule_post_start))

    _LOGGER.info(
        "YouTube-DLP core ready without startup I/O: output=%s library=%s",
        download_path,
        library_path,
    )
    return True


async def _async_start_optional_runtime(
    hass: HomeAssistant,
    entry: ConfigEntry,
    manager: YoutubeDlpManager,
) -> None:
    """Start the only remaining post-start convenience: playback resume events."""
    if getattr(entry, "runtime_data", None) is not manager:
        return

    playback = getattr(manager, "playback_manager", None)
    if isinstance(playback, PlaybackManager):
        try:
            playback.async_start_resume_monitoring()
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Playback resume monitoring failed to start")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload runtime managers without unregistering global services."""
    manager = getattr(entry, "runtime_data", None)
    if isinstance(manager, YoutubeDlpManager):
        playback = getattr(manager, "playback_manager", None)
        if isinstance(playback, PlaybackManager):
            playback.async_stop_resume_monitoring()

        await manager.async_shutdown()

    hass.states.async_remove(STATE_DOWNLOADER)
    return True
