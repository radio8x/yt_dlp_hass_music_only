# Bản tùy biến "chỉ yt_dlp.play" — tóm tắt kết quả

## Chỉ còn 1 service duy nhất: `yt_dlp.play`
Vào Developer Tools → Actions, gõ "yt_dlp" chỉ nên thấy đúng 1 dòng.

## Các file đã bị XÓA hoàn toàn khỏi mã nguồn
- download_services.py, download_runtime.py, runtime.py (tải xuống)
- favorites.py, favorites_playback.py, favorites_runtime.py, favorites_services.py (yêu thích)
- target_services.py, tv_playback.py (tự động chọn thiết bị / phát lên TV)
- frontend.py và thư mục frontend/ (thẻ giao diện Lovelace, JS 148K)

## Các file vẫn còn nhưng KHÔNG chạy (giữ để tương thích nội bộ, không xóa được an toàn)
- dlna.py, dlna_runtime.py — do media_source.py (module lõi HA) vẫn tham chiếu tới
- media_targets.py — do config_flow.py (màn hình cài đặt) vẫn tham chiếu tới
Các file này không được gọi tới trong luồng chạy thực tế nữa, không tốn CPU/RAM.

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

## __init__.py — viết lại hoàn toàn sạch
Không còn dòng comment thừa, không import module đã xóa, chỉ đăng ký:
- 2 HTTP view (media/stream) để phát luồng
- Service `yt_dlp.play`
- Theo dõi resume playback (tính năng lõi giữ nguyên trạng thái khi mất kết nối tạm thời)

## Cách cài lên Home Assistant (thay thế bản cũ)
1. Xóa toàn bộ thư mục `/config/custom_components/yt_dlp` cũ trên HA
2. Copy toàn bộ thư mục `custom_components/yt_dlp` trong file zip này vào đúng vị trí đó
3. Khởi động lại Home Assistant HOÀN TOÀN (không chỉ reload integration)
4. Kiểm tra: Developer Tools → Actions → gõ "yt_dlp" → chỉ còn `yt_dlp.play`

## Đẩy lên GitHub (fork radio8x/yt_dlp_hass_music_only)
Trên máy Windows, trong thư mục đã clone fork:
1. Xóa các file/thư mục đã liệt kê ở mục "Các file đã bị XÓA" phía trên
2. Copy đè `__init__.py`, `services.yaml`, `play_services.py` từ file zip này vào
3. Chạy:
```
git add -A
git commit -m "Xoa toan bo file khong dung, chi giu yt_dlp.play"
git push origin main
```
4. Tạo release mới trên GitHub (vd v2.0.0)
5. Vào HACS trên HA → bấm Update → khởi động lại HA
