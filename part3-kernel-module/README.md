# Phần 3 — Kernel Module: Networking

Triển khai đầy đủ **5 bài tập** của lab Networking (Linux Kernel Labs), mỗi bài là một module độc lập.

| Bài | File | Nội dung |
|---|---|---|
| 1 | `net_monitor.c` | Giám sát & log packet TCP/UDP/ICMP qua netfilter hook |
| 2 | `net_filter.c` + `filter_ctl.c` | Lọc (DROP) packet theo IP đích, cấu hình qua **ioctl** |
| 3+4 | `ksock_tcp.c` | Tạo socket TCP **trong kernel**, listen cổng 60000, accept & đọc dữ liệu |
| 5 | `ksock_udp.c` | Gửi tin nhắn **UDP từ kernel** (`kernel_sendmsg`) |

## Kiến thức áp dụng

- **Netfilter**: `struct nf_hook_ops`, `nf_register_net_hook()`, `NF_ACCEPT`/`NF_DROP`
- **sk_buff**: `ip_hdr()`, `tcp_hdr()`, `udp_hdr()` đọc header gói tin
- **Kernel socket**: `sock_create_kern()`, `kernel_bind/listen/accept`, `kernel_recvmsg/sendmsg`
- **Misc device + ioctl**: giao tiếp user-space ↔ kernel để cấu hình
- **kthread**: chạy server lắng nghe trong kernel thread

## Build tất cả

```bash
make            # tạo *.ko + công cụ filter_ctl
make clean
```

## Chạy từng bài

### Bài 1 — Giám sát packet
```bash
sudo insmod net_monitor.ko
sudo dmesg -w
ping -c2 8.8.8.8 ; curl -s http://example.com >/dev/null   # sinh lưu lượng
sudo rmmod net_monitor
```

### Bài 2 — Lọc theo IP đích (ioctl)
```bash
sudo insmod net_filter.ko
sudo ./filter_ctl set 8.8.8.8     # chặn gói đến 8.8.8.8
ping -c3 8.8.8.8                  # -> 100% packet loss; xem 'DROP' trong dmesg
sudo ./filter_ctl clear           # bỏ chặn
sudo rmmod net_filter
```

### Bài 3+4 — TCP listen/accept trong kernel
```bash
sudo insmod ksock_tcp.ko
sudo dmesg -w                     # cửa sổ 1
# cửa sổ 2:
echo "hello kernel" | nc 127.0.0.1 60000
# -> dmesg in ra dữ liệu nhận được
sudo rmmod ksock_tcp
```

### Bài 5 — Gửi UDP từ kernel
```bash
# Cửa sổ 1: mở listener trước
nc -u -l 5005
# Cửa sổ 2:
sudo insmod ksock_udp.ko dip="127.0.0.1" dport=5005 msg="Xin chao tu kernel"
# -> listener nhận được chuỗi; dmesg báo "da gui N byte"
sudo rmmod ksock_udp
```

## Lưu ý quan trọng

- **Snapshot VMware trước khi `insmod`** — lỗi kernel có thể panic máy ảo.
- Luôn `rmmod` trước khi tắt máy/sửa code.
- API có thể đổi giữa các phiên bản kernel. Code này dùng API kernel **≥ 5.x**
  (đã test trên Ubuntu 22.04 / kernel 5.15). Nếu kernel quá mới/cũ, một vài hàm
  (`kernel_accept` flags, `sock_create_kern`) có thể cần chỉnh nhẹ.
- Nếu file bị lỗi ký tự `\r` (do tạo trên Windows): `dos2unix *.c Makefile`.
