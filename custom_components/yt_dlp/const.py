"""Constants for the YouTube-DLP integration."""

from __future__ import annotations

DOMAIN = "yt_dlp"
VERSION = "0.5.28"

STATE_DOWNLOADER = f"{DOMAIN}.downloader"

SERVICE_PLAY = "play"

ATTR_URL = "url"
ATTR_MEDIA_PLAYER = "media_player"

MEDIA_TYPE_AUDIO = "audio"

CONF_MEDIA_LIBRARY_PATH = "media_library_path"

DEFAULT_FILENAME_TEMPLATE = "%(title).180B [%(id)s].%(ext)s"
TEMP_DIR_NAME = ".yt_dlp_tmp"
CACHE_DIR_NAME = ".yt_dlp_cache"

MAX_CONCURRENT_DOWNLOADS = 2
MAX_CONCURRENT_SEARCHES = 2
MAX_RETAINED_JOBS = 50

# Options-flow notification settings vẫn được manager.py/notifications.py sử dụng
# ở phần code tải xuống nội bộ (không còn service nào gọi tới, nhưng để nguyên
# cho manager.py không bị lỗi import — xem CHANGES_VI.md).
SECTION_NOTIFY_HOME_ASSISTANT = "notify_home_assistant"
SECTION_NOTIFY_MOBILE = "notify_mobile"
SECTION_NOTIFY_ZALO = "notify_zalo"

CONF_NOTIFY_ENABLED = "enabled"
CONF_MOBILE_NOTIFY_ACTION = "mobile_notify_action"
CONF_ZALO_THREAD_ID = "thread_id"
CONF_ZALO_ACCOUNT = "account_selection"
CONF_ZALO_TYPE = "type"

ZALO_TYPE_GROUP = "group"
ZALO_SERVICE_DOMAIN = "zalo_bot"
ZALO_SERVICE_SEND_MESSAGE = "send_message"
