# Phần 4 — Web Dashboard (demo bổ trợ)

Bảng điều khiển web tối giản (Flask) để demo module nhân trực quan:
xem log `dmesg` realtime, load/unload `steg_net` — tất cả từ trình duyệt.

> Đây là phần **demo bổ trợ**, không bắt buộc. Backend chạy trên chính máy Ubuntu
> và là cầu nối trình duyệt ↔ hệ thống.

## Kiến trúc

```
Trình duyệt ── HTTP/SSE ──► Flask (app.py) ──► subprocess ──► insmod/rmmod/dmesg
```

| Endpoint | Chức năng |
|---|---|
| `GET  /` | Trang dashboard |
| `GET  /api/status` | Module nào đang nạp (`lsmod`) |
| `POST /api/module/load/<name>` | `insmod <name>.ko` |
| `POST /api/module/unload/<name>` | `rmmod <name>` |
| `GET  /api/dmesg/stream` | Stream `dmesg --follow` realtime (SSE) |
| `GET  /api/processes` | Top tiến trình theo CPU |

> Module được whitelist trong `app.py` — hiện chỉ cho phép `steg_net`.

## Cài & chạy

```bash
# 1) Build kernel module trước
cd ../part3-kernel-module && make && cd ../part4-web

# 2) Cài Flask
pip3 install flask
# hoặc: sudo apt install -y python3-flask

# 3) Chạy
python3 app.py
```

Mở trình duyệt: **http://127.0.0.1:5000**

Muốn xem từ máy host (VM chạy headless): dùng IP của VM, vd `http://192.168.x.x:5000`.

## Cấu hình sudoers (chạy lệnh không hỏi mật khẩu)

`insmod`/`rmmod`/`dmesg` cần root. Cho phép user hiện tại chạy không cần mật khẩu
(**chỉ làm trên VM demo**):

```bash
sudo visudo -f /etc/sudoers.d/dautai42
```

Thêm (thay `your_user` bằng username của bạn):

```
your_user ALL=(root) NOPASSWD: /usr/sbin/insmod, /usr/sbin/rmmod, /usr/bin/dmesg
```

> Kiểm tra đường dẫn thực tế: `which insmod` (có thể là `/sbin/insmod`).

## Lưu ý

- `debug=True` chỉ để phát triển; **không expose ra Internet** (web này chạy lệnh hệ thống).
- Nếu log dmesg trống: kiểm tra quyền `sudo dmesg --follow`.
