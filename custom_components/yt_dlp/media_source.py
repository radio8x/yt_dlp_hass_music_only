"""Media Source platform: resolve a `yt_dlp.play` stream token to a playable URL.

Bản tùy biến: không còn thư viện nhạc local (đã bỏ scan_library/favorites) và
không còn đường DLNA (đã bỏ target_services/dlna). Chỉ còn một việc duy nhất:
khi media_player.play_media được gọi với media-source://yt_dlp/stream/<token>,
trả về URL relay HTTP thật sự để trình phát mở.
"""

from __future__ import annotations

import logging
from urllib.parse import unquote

from homeassistant.components.media_source import (
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.network import NoURLAvailableError, get_url

from .const import DOMAIN
from .playback import STREAM_MEDIA_SOURCE_PREFIX, STREAM_URL_PREFIX

_LOGGER = logging.getLogger(__name__)


async def async_get_media_source(hass: HomeAssistant) -> MediaSource:
    """Return the YouTube-DLP media source."""
    return YoutubeDlpMediaSource(hass)


class YoutubeDlpMediaSource(MediaSource):
    """Resolve yt_dlp.play stream tokens to the HTTP relay endpoint."""

    name = "YouTube-DLP"

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(DOMAIN)
        self.hass = hass

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Resolve a stream token to the integration's playback HTTP endpoint."""
        from . import get_playback_manager

        relative = unquote(item.identifier)
        if not relative.startswith(STREAM_MEDIA_SOURCE_PREFIX):
            raise Unresolvable("Unknown media source identifier")

        token = relative.removeprefix(STREAM_MEDIA_SOURCE_PREFIX)
        if not token or "/" in token:
            raise Unresolvable("Invalid playback stream")

        manager = get_playback_manager(self.hass)
        stream_session = manager.get_stream_session(token)
        if stream_session is None:
            raise Unresolvable("Playback stream has expired")

        # This is an unguessable capability URL. The harmless query string
        # deliberately prevents Home Assistant from appending authSig, which
        # can make Cast media URLs unnecessarily long. A filename suffix also
        # helps strict receivers infer the container before the first bytes.
        stream_path = (
            f"{STREAM_URL_PREFIX}/{token}"
            f"{_stream_suffix(stream_session.info.mime_type)}?source=yt_dlp"
        )

        # MediaSourceItem tells us the actual target. Cast devices sometimes
        # cannot reach HA's detected LAN URL (VLAN/client isolation is common),
        # while the configured external or Home Assistant Cloud URL is usable.
        # Prefer that public route only for Cast; otherwise keep the local path.
        if _is_cast_target(self.hass, item.target_media_player):
            try:
                base_url = get_url(self.hass, prefer_external=True, prefer_cloud=True)
            except NoURLAvailableError:
                pass
            else:
                return PlayMedia(
                    f"{base_url.rstrip('/')}{stream_path}",
                    stream_session.info.mime_type,
                )

        return PlayMedia(stream_path, stream_session.info.mime_type)


def _is_cast_target(hass: HomeAssistant, entity_id: str | None) -> bool:
    """Return whether a Media Source request targets Home Assistant Cast."""
    if not entity_id:
        return False
    entry = er.async_get(hass).async_get(entity_id)
    return entry is not None and entry.platform == "cast"


def _stream_suffix(mime_type: str) -> str:
    """Return a cosmetic extension for receivers that inspect the URL path."""
    base = mime_type.split(";", 1)[0].strip().lower()
    return {
        "audio/mp4": ".m4a",
        "audio/webm": ".webm",
        "audio/ogg": ".ogg",
        "audio/mpeg": ".mp3",
        "audio/flac": ".flac",
        "audio/wav": ".wav",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
    }.get(base, ".media")
