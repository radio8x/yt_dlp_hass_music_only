# Bản tùy biến "chỉ yt_dlp.play" — dọn sạch toàn diện (v3)

## Chỉ còn 1 service: `yt_dlp.play`, không màn hình thiết lập
- Thêm integration: tự động tạo cấu hình ngay, không hỏi gì
- Không có nút "Configure" (đã bỏ toàn bộ Options flow: thư mục, thông báo Zalo/mobile, media targets)

## File đã XÓA (so với bản gốc, tổng cộng 15 file + 1 thư mục)
download_services.py, download_runtime.py, runtime.py, favorites.py,
favorites_playback.py, favorites_runtime.py, favorites_services.py,
target_services.py, tv_playback.py, frontend.py, frontend/ (thư mục),
dlna.py, dlna_runtime.py, media_targets.py

## File đã viết lại gọn hơn nhiều
- `__init__.py` — chỉ đăng ký 1 HTTP view (stream relay) + service `play`
- `config_flow.py` — từ 587 dòng còn ~30 dòng, chỉ tự tạo entry
- `play_services.py` — chỉ còn hàm `async_play`, bỏ `play_multi`/`scan_library`
- `media_source.py` — chỉ còn nhánh resolve stream token, bỏ nhánh DLNA + thư viện local
- `media_http.py` — bỏ `YoutubeDlpMediaView` (phục vụ file local), chỉ giữ `YoutubeDlpStreamView` (relay)
- `const.py` — từ ~90 hằng số còn ~20, chỉ giữ cái thực sự được dùng

## File vẫn còn NHƯNG phần lớn không chạy (không xóa an toàn được)
- `manager.py` (54K) — vẫn tồn tại vì `yt_dlp.play` cần nó làm "vỏ chứa" runtime,
  nhưng toàn bộ logic tải xuống bên trong không bao giờ được gọi tới nữa
  (service download đã xóa). Không gỡ tiếp phần này vì rủi ro làm hỏng cả
  `play` chỉ để tiết kiệm vài chục KB code chết.
- `notifications.py` — vẫn được `manager.py` import ở nhánh code chết nói trên,
  không thể xóa nếu không viết lại `manager.py`.

## services.yaml — chỉ còn
```yaml
play:
  fields:
    url:
      required: true
      selector:
        text:
          type: url
    media_player:
      required: true
      selector:
        entity:
          domain: media_player
          multiple: false
```

## Cách cài lên Home Assistant
1. Nếu đã có tích hợp "YouTube-DLP" cũ: Settings → Devices & services →
   YouTube-DLP → ⋮ → Delete (xóa cấu hình cũ, vì config data đã đổi cấu trúc)
2. Copy toàn bộ `custom_components/yt_dlp` trong zip này, ghi đè vào
   `/config/custom_components/yt_dlp`
3. Khởi động lại Home Assistant HOÀN TOÀN
4. Settings → Devices & services → Add integration → tìm "YouTube-DLP" →
   tự động thêm ngay, không hỏi gì
5. Kiểm tra: Developer Tools → Actions → gõ "yt_dlp" → chỉ còn `yt_dlp.play`

## Đẩy lên GitHub fork (radio8x/yt_dlp_hass_music_only)
Trong thư mục repo đã clone trên Windows:
1. Xóa hết nội dung cũ (giữ lại thư mục `.git`)
2. Giải nén zip này, copy toàn bộ nội dung bên trong thư mục
   `yt_dlp_hass_music_only` vào đúng chỗ vừa xóa
3. `git add -A`
4. `git commit -m "Don sach toan dien: bo man hinh thiet lap, chi con play"`
5. `git push origin main`
6. Tạo release mới (v3.0.0) → HACS Update → restart HA
