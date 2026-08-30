"""Protected speaker service boundary.

This module never imports the download worker or Favorites controller. It is
the only service layer allowed to turn a remote URL into media_player playback.
Bản tùy biến: chỉ còn duy nhất service `play`.
"""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components.media_player import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_EXTRA,
    SERVICE_PLAY_MEDIA,
)
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError

from .const import ATTR_MEDIA_PLAYER, ATTR_URL, DOMAIN, SERVICE_PLAY
from .play_runtime import get_playback_manager
from .service_validation import http_url, media_player_entity

PLAY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_URL): http_url,
        vol.Required(ATTR_MEDIA_PLAYER): media_player_entity,
    }
)


def async_register_play_services(hass: HomeAssistant) -> None:
    """Register the protected direct speaker playback service."""

    async def async_play(call: ServiceCall) -> ServiceResponse | None:
        playback = get_playback_manager(hass)
        entity_id = call.data[ATTR_MEDIA_PLAYER]
        try:
            info, media_source_id = await playback.async_create_stream(call.data[ATTR_URL])
            metadata: dict[str, object] = {"title": info.title}
            if info.artist:
                metadata["artist"] = info.artist
            if info.thumbnail:
                metadata["images"] = [{"url": info.thumbnail}]

            await hass.services.async_call(
                "media_player",
                SERVICE_PLAY_MEDIA,
                service_data={
                    ATTR_MEDIA_CONTENT_ID: media_source_id,
                    ATTR_MEDIA_CONTENT_TYPE: info.mime_type,
                    ATTR_MEDIA_EXTRA: {"metadata": metadata},
                },
                target={"entity_id": entity_id},
                blocking=True,
                context=call.context,
            )
            playback.async_track_remote_playback(
                entity_id, call.data[ATTR_URL], info, media_source_id
            )
        except HomeAssistantError:
            raise
        except Exception as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="play_failed",
                translation_placeholders={"error": str(err)},
            ) from err

        response = {"media_player": entity_id, **info.as_dict()}
        return response if call.return_response else None

    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY,
        async_play,
        schema=PLAY_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
