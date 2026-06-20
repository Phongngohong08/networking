# Đề tài 42 — Lập trình nhân Linux

Môn: **Lập trình nhân Linux** — L02 — 2026

## Thành viên nhóm

| Họ tên | MSSV | Lớp |
|---|---|---|
| Ngô Minh Cường | CT070306 | L02 |
| Ngô Hồng Phong | CT070337 | L01 |
| Đỗ Minh Thuần  | CT070353 | L01 |

## Nội dung đề tài

Đề tài gồm **3 phần** theo yêu cầu môn học:

### Phần 1 — Shell scripting (`part1-shell/`)
Lập trình Bash tự động hóa quản trị hệ thống:
- `file_manager.sh` — quản lý file/thư mục, sao lưu nén
- `scheduler.sh` — lập lịch định kỳ (cron) và một lần (at)
- `set_time.sh` — thiết lập thời gian, múi giờ, đồng bộ NTP
- `pkg_manager.sh` — cài/gỡ phần mềm tự động qua apt

### Phần 2 — Lập trình user-space (`part2-userspace/`)
Quản lý tiến trình, file và socket mạng trong C (POSIX/syscall):
- `proc_info.c` — đọc `/proc/<pid>/status`, liệt kê tiến trình
- `file_ops.c` — `open/read/write/stat` thao tác file
- `tcp_server.c` / `tcp_client.c` — socket TCP echo

### Phần 3 — Kernel module (`part3-kernel-module/`) — *TRỌNG TÂM*

Module nhân `steg_net.ko`: **giấu tin trong gói TCP** (network steganography).

Kỹ thuật: nhúng từng byte của thông điệp bí mật vào trường **IP Identification**
(16-bit) của mỗi gói TCP. Byte cao = `0xAB` (magic marker), byte thấp = ký tự cần giấu.
Phía nhận đọc IP ID và tái tạo thông điệp.

```
IP_ID = 0xAB48  →  ký tự 'H' (0x48)
IP_ID = 0xAB45  →  ký tự 'E' (0x45)
IP_ID = 0xAB4C  →  ký tự 'L' ...
```

Sử dụng hai Netfilter hook:
- `NF_INET_LOCAL_OUT` — nhúng tin vào gói TCP đi ra
- `NF_INET_PRE_ROUTING` — trích xuất từ gói TCP đến

Theo dõi qua `/proc/steg_net`.

## Cấu trúc thư mục

```
networking/
├── README.md
├── part1-shell/
│   ├── file_manager.sh
│   ├── scheduler.sh
│   ├── set_time.sh
│   └── pkg_manager.sh
├── part2-userspace/
│   ├── Makefile
│   ├── proc_info.c
│   ├── file_ops.c
│   ├── tcp_server.c
│   └── tcp_client.c
├── part3-kernel-module/        ← MODULE NHÂN (trọng tâm)
│   ├── steg_net.c              ← module giấu tin trong TCP
│   └── Makefile
└── docs/
    ├── BAOCAO.md               ← nguồn báo cáo (Markdown)
    ├── build_docx.py           ← sinh BaoCao_DeTai42_Networking.docx
    └── build_pptx.py           ← sinh ThuyetTrinh_DeTai42_Networking.pptx
```

## Thiết lập VM từ đầu

> Chạy trên **Ubuntu 22.04 LTS** trong VMware/VirtualBox. Cần quyền root.

**Bước 1 — Cập nhật & công cụ cơ bản**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl net-tools build-essential dos2unix
```

**Bước 2 — Build kernel module (Phần 3)**
```bash
sudo apt install -y gcc make linux-headers-$(uname -r)
# Kiểm tra: ls /lib/modules/$(uname -r)/build  (phải có thư mục này)
```

**Bước 3 — Python (sinh tài liệu)**
```bash
sudo apt install -y python3 python3-pip
pip3 install python-docx python-pptx
```

**Bước 4 — Gói at (lập lịch một lần, Phần 1)**
```bash
sudo apt install -y at && sudo systemctl enable --now atd
```

**Kéo dự án**
```bash
git clone <URL-repo> networking
cd networking
# Xử lý ký tự \r nếu file tạo trên Windows:
find . -type f \( -name "*.sh" -o -name "*.c" -o -name "Makefile" -o -name "*.py" \) \
  -exec dos2unix {} +
```

**Kiểm tra nhanh**
```bash
gcc --version | head -1
ls /lib/modules/$(uname -r)/build
python3 -c "import docx, pptx; print('python-docx, python-pptx ok')"
```

## Chạy nhanh

```bash
# Phần 1
cd part1-shell && chmod +x *.sh && ./file_manager.sh

# Phần 2
cd part2-userspace && make
./tcp_server 60000 &  &&  ./tcp_client 127.0.0.1 60000

# Phần 3 — module nhân (trọng tâm)
cd part3-kernel-module && make
sudo insmod steg_net.ko peer_ip=127.0.0.1 'secret="HELLO"'
# terminal 1: nc -l 7777
# terminal 2: echo test | nc 127.0.0.1 7777
sudo dmesg | grep steg
cat /proc/steg_net
sudo rmmod steg_net

# Tài liệu
cd docs
python3 build_docx.py   # → BaoCao_DeTai42_Networking.docx
python3 build_pptx.py   # → ThuyetTrinh_DeTai42_Networking.pptx
```

## Cảnh báo

- Code kernel chạy ở **ring 0**: lỗi có thể crash/panic máy ảo.
- Luôn **snapshot trước khi `insmod`**.
- Luôn `sudo rmmod steg_net` trước khi sửa code và build lại.
