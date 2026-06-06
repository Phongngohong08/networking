# Đề tài 42 — Lập trình nhân Linux: Networking

Môn: **Lập trình nhân Linux** — L02 — 2026

Tham khảo phần kernel module: [Linux Kernel Labs — Networking](https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html)

## Thành viên nhóm

| Họ tên | MSSV | Lớp |
|---|---|---|
| Ngô Minh Cường | CT070306 | L02 |
| Ngô Hồng Phong | CT070337 | L01 |
| Đỗ Minh Thuần  | CT070353 | L01 |

## Mục tiêu đề tài

Đề tài gồm **3 phần** theo yêu cầu chung của môn học:

1. **Phần 1 — Shell scripting** (`part1-shell/`)
   Lập trình shell để: quản lý file, lập lịch tác vụ (cron/at), thiết lập thời gian hệ thống,
   cài đặt/gỡ bỏ chương trình tự động.

2. **Phần 2 — Lập trình user-space** (`part2-userspace/`)
   Quản lý tiến trình, file, **socket và network** trong Ubuntu (C, dùng syscall/POSIX).

3. **Phần 3 — Kernel module: Networking** (`part3-kernel-module/`) — *phần trọng tâm*
   Viết mô-đun nhân và tích hợp vào hệ thống. Triển khai **đủ 5 bài** của lab:
   - Bài 1: Bắt/giám sát packet bằng **netfilter hooks** (`sk_buff`, `ip_hdr/tcp_hdr/udp_hdr`)
   - Bài 2: Lọc packet theo địa chỉ đích, cấu hình qua **ioctl**
   - Bài 3+4: Tạo socket trong kernel (`sock_create_kern`), **listen/accept TCP** cổng 60000
   - Bài 5: **Gửi UDP từ kernel** (`kernel_sendmsg`)

4. **Phần 4 — Web dashboard** (`part4-web/`) — *demo bổ trợ*
   Bảng điều khiển Flask: load/unload module, xem **log dmesg realtime**, cấu hình
   lọc IP — tất cả từ trình duyệt. Backend chạy lệnh hệ thống qua subprocess.

## Môi trường chạy

> Chạy trên **Ubuntu** (khuyến nghị 22.04 LTS) trong **VMware** hoặc GCP VM. Cần quyền root.

### Thiết lập VM mới từ đầu (chạy 1 lần)

Sau khi cài Ubuntu sạch trên VMware, mở Terminal và chạy lần lượt:

**Bước 1 — Cập nhật hệ thống & cài công cụ cơ bản**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl net-tools build-essential
```

**Bước 2 — Cài công cụ build kernel module (Phần 3) + biên dịch C (Phần 2)**
```bash
sudo apt install -y gcc make linux-headers-$(uname -r)
```
> Gói `linux-headers-$(uname -r)` phải **khớp đúng** kernel đang chạy mới build được module.
> Kiểm tra: `uname -r` rồi `ls /lib/modules/$(uname -r)/build` (phải tồn tại).
> Nếu báo thiếu, thử: `sudo apt install -y linux-headers-generic` và **khởi động lại** VM.

**Bước 3 — Cài Python & Flask (Phần 4 — web dashboard)**
```bash
sudo apt install -y python3 python3-pip
pip3 install flask
# Nếu Ubuntu chặn pip cài toàn cục (lỗi "externally-managed-environment"):
#   sudo apt install -y python3-flask
```

**Bước 4 — Cài 'at' cho phần lập lịch (Phần 1)**
```bash
sudo apt install -y at && sudo systemctl enable --now atd
```

### Kéo dự án về (git clone)

```bash
# Thay <URL-repo> bằng link repo của nhóm (GitHub/GitLab)
cd ~
git clone <URL-repo> networking
cd networking
```

> Lần đầu dùng git, cấu hình danh tính (commit mới ghi đúng tên):
> ```bash
> git config --global user.name  "Ten cua ban"
> git config --global user.email "email@cua.ban"
> ```

> File tạo trên Windows có thể dính ký tự xuống dòng `\r`. Sau khi clone, chạy 1 lần:
> ```bash
> sudo apt install -y dos2unix
> find . -type f \( -name "*.sh" -o -name "*.c" -o -name "Makefile" -o -name "*.py" \) -exec dos2unix {} +
> ```

### Kiểm tra nhanh đã sẵn sàng chưa

```bash
git --version && gcc --version | head -1 && make --version | head -1
python3 --version && python3 -c "import flask; print('flask', flask.__version__)"
ls /lib/modules/$(uname -r)/build  # in ra đường dẫn => OK để build module
```

## Cấu trúc thư mục

```
networking/
├── README.md                 # file này
├── part1-shell/              # Phần 1: shell scripts
│   ├── README.md
│   ├── file_manager.sh
│   ├── scheduler.sh
│   ├── set_time.sh
│   └── pkg_manager.sh
├── part2-userspace/          # Phần 2: chương trình C user-space
│   ├── README.md
│   ├── Makefile
│   ├── proc_info.c           # quản lý tiến trình
│   ├── file_ops.c            # thao tác file
│   ├── tcp_server.c          # socket server
│   └── tcp_client.c          # socket client
└── part3-kernel-module/      # Phần 3: kernel module networking (5 bài lab)
    ├── README.md
    ├── Makefile
    ├── net_monitor.c         # Bài 1: netfilter hook log packet TCP/UDP/ICMP
    ├── net_filter.c          # Bài 2: lọc packet theo IP đích (ioctl)
    ├── filter_ctl.c          # công cụ user-space điều khiển net_filter
    ├── ksock_tcp.c           # Bài 3+4: TCP listen/accept trong kernel
    └── ksock_udp.c           # Bài 5: gửi UDP từ kernel
│
└── part4-web/                # Phần 4: web dashboard demo (Flask)
    ├── app.py                # backend: load/unload, stream dmesg, filter
    ├── templates/index.html
    ├── static/{style.css,app.js}
    ├── requirements.txt
    └── README.md             # cách chạy + cấu hình sudoers
```

## Cách build & chạy nhanh

```bash
# Phần 2 (user-space)
cd part2-userspace && make
./tcp_server 60000          # cửa sổ 1
./tcp_client 127.0.0.1 60000  # cửa sổ 2

# Phần 3 (kernel module)
cd part3-kernel-module && make
sudo insmod net_monitor.ko
sudo dmesg -w               # xem log packet bắt được
sudo rmmod net_monitor      # gỡ module
```

Xem `README.md` trong từng thư mục con để biết chi tiết.

## Cảnh báo an toàn

- Code kernel chạy ở ring 0: lỗi có thể **treo/panic máy ảo**. Luôn test trong VM, **snapshot trước khi insmod**.
- Luôn `rmmod` module trước khi tắt máy/sửa code.
