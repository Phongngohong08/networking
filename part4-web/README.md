# Phần 4 — Web Dashboard (demo & điều khiển)

Bảng điều khiển web tối giản (Flask) để demo dự án trực quan: load/unload kernel
module, **xem log dmesg realtime**, cấu hình lọc IP — tất cả từ trình duyệt.

> Đây là phần **demo bổ trợ**. Backend chạy trên chính máy Ubuntu và là cầu nối
> trình duyệt ↔ hệ thống (insmod/rmmod/dmesg/filter_ctl).

## Kiến trúc

```
Trình duyệt ── HTTP/SSE ──► Flask (app.py) ──► subprocess ──► insmod/rmmod/dmesg/filter_ctl
```

| Endpoint | Chức năng |
|---|---|
| `GET  /` | Trang dashboard |
| `GET  /api/status` | Module nào đang Loaded (đọc `lsmod`) |
| `POST /api/module/load|unload/<name>` | insmod / rmmod module |
| `POST /api/filter` | gọi `filter_ctl set <ip>` / `clear` (Bài 2) |
| `GET  /api/dmesg/stream` | stream `dmesg --follow` realtime (SSE) |
| `GET  /api/processes` | top tiến trình theo CPU |

## Cài & chạy

```bash
# 1) Build kernel module trước (để có file .ko)
cd ../part3-kernel-module && make && cd ../part4-web

# 2) Cài Flask
pip3 install -r requirements.txt   # hoặc: sudo apt install python3-flask

# 3) Chạy
python3 app.py
```

Mở trình duyệt: **http://127.0.0.1:5000**
(Chạy trong VM nhưng muốn xem từ máy host: dùng IP của VM, vd `http://192.168.x.x:5000`.)

## Cấu hình sudoers (để web chạy lệnh không hỏi mật khẩu)

Các thao tác `insmod/rmmod/dmesg/filter_ctl` cần root. Cho phép user hiện tại chạy
chúng không cần mật khẩu — **chỉ làm trên VM demo, không làm trên máy thật**:

```bash
sudo visudo -f /etc/sudoers.d/dautai42
```

Thêm (thay `your_user` bằng user của bạn, sửa đường dẫn `filter_ctl` cho đúng):

```
your_user ALL=(root) NOPASSWD: /usr/sbin/insmod, /usr/sbin/rmmod, /usr/bin/dmesg, /home/your_user/.../part3-kernel-module/filter_ctl
```

> `insmod/rmmod` có thể nằm ở `/sbin/...` tùy bản Ubuntu — kiểm tra bằng `which insmod`.

## Lưu ý

- `debug=True` chỉ để phát triển. Demo trong mạng nội bộ thì ổn; **đừng expose ra Internet**
  (web này chạy lệnh hệ thống — rủi ro cao nếu mở công khai).
- Tên module được **whitelist** trong `app.py` và IP được validate → tránh truyền lệnh tùy ý.
- Nếu log dmesg trống: bấm tắt "Chỉ hiện log module dự án", hoặc kiểm tra quyền chạy
  `sudo dmesg --follow`.
