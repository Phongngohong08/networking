# Phần 1 — Shell scripting

Các script quản trị hệ thống cơ bản.

| Script | Chức năng |
|---|---|
| `file_manager.sh` | Quản lý file/thư mục (menu: liệt kê, tạo, xóa, tìm, sao lưu) |
| `scheduler.sh`    | Lập lịch tác vụ bằng `cron`/`at` |
| `set_time.sh`     | Xem/thiết lập thời gian, NTP, múi giờ (`timedatectl`) |
| `pkg_manager.sh`  | Cài đặt/gỡ bỏ chương trình tự động (`apt`) |

## Chuẩn bị

```bash
chmod +x *.sh
# scheduler 'once' cần gói at:
sudo apt install -y at && sudo systemctl enable --now atd
```

## Ví dụ

```bash
./file_manager.sh                          # menu quản lý file
./scheduler.sh add "*/5 * * * *" "date >> /tmp/tick.log"
./scheduler.sh list
./set_time.sh show
./set_time.sh zone Asia/Ho_Chi_Minh
./pkg_manager.sh install htop net-tools
echo -e "htop\ntree\ncurl" > pkgs.txt && ./pkg_manager.sh batch pkgs.txt
```

> Hầu hết thao tác thay đổi hệ thống cần `sudo`.
