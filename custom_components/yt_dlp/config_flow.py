"""Config flow for YouTube-DLP.

Bản tùy biến: chỉ dùng service `yt_dlp.play`. Không có màn hình thiết lập nào
được hỏi — tích hợp tự tạo cấu hình ngay khi được thêm vào, và không có
Options flow (không còn thư mục tải xuống, thông báo, hay media targets để
cấu hình).
"""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_FILE_PATH

from .const import CONF_MEDIA_LIBRARY_PATH, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle YouTube-DLP configuration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Tự động tạo cấu hình, không hỏi gì cả."""
        await self.async_set_unique_id(f"{DOMAIN}.downloader")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="YouTube-DLP",
            data={
                CONF_FILE_PATH: "yt_dlp_unused",
                CONF_MEDIA_LIBRARY_PATH: "yt_dlp_unused",
            },
        )
