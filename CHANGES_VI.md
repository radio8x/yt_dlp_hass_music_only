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

