# Phần 3 — Kernel Module: Giấu tin trong gói TCP

Module nhân duy nhất `steg_net.ko` thực hiện kỹ thuật **network steganography**:
nhúng thông điệp bí mật vào trường **IP Identification** của gói TCP, và trích xuất
thông điệp từ phía nhận — toàn bộ ở mức nhân thông qua Netfilter hook.

## Nguyên lý

```
IP ID (16-bit):
┌──────────────────┬────────────────────┐
│  Byte cao = 0xAB │  Byte thấp = ký tự │
│  (magic marker)  │  secret[pos]        │
└──────────────────┴────────────────────┘

Ví dụ: secret="HELLO"
  Gói 1 → IP_ID = 0xAB48  ('H')
  Gói 2 → IP_ID = 0xAB45  ('E')
  ...
```

## Tham số module

| Tham số | Mô tả | Mặc định |
|---|---|---|
| `peer_ip` | IP đích (embed) / IP nguồn (extract) — **bắt buộc** | — |
| `secret` | Thông điệp cần giấu | `"Hello from kernel!"` |

## Build

```bash
# Cài phụ thuộc (1 lần)
sudo apt install -y build-essential linux-headers-$(uname -r)

# Build
make            # → steg_net.ko

# Dọn dẹp
make clean
```

## Chạy demo (một VM, loopback)

```bash
# Bước 1 — nạp module
sudo insmod steg_net.ko peer_ip=127.0.0.1 'secret="HELLO"'

# Bước 2 — mở listener (terminal 1)
nc -l 7777

# Bước 3 — gửi dữ liệu TCP (terminal 2)
echo "test" | nc 127.0.0.1 7777

# Bước 4 — xem log embed/extract
sudo dmesg | grep steg

# Bước 5 — xem trạng thái realtime
cat /proc/steg_net

# Bước 6 — gỡ module (in thông điệp trích xuất)
sudo rmmod steg_net
sudo dmesg | tail -5
```

### Ví dụ log dmesg

```
steg_net: loaded — secret="HELLO" peer=127.0.0.1
steg [EMBED] pos=0  char='H'(0x48)  IP_ID=0xAB48  -> 127.0.0.1
steg [EMBED] pos=1  char='E'(0x45)  IP_ID=0xAB45  -> 127.0.0.1
steg [EXTRACT] IP_ID=0xAB48  char='H'  from 127.0.0.1
steg_net: đã trích xuất: "HELLO"
```

### /proc/steg_net

```
=== steg_net status ===
secret    : "HELLO"  (5 bytes)
peer_ip   : 127.0.0.1
magic     : 0xAB
embed_pos : 2  (ký tự tiếp theo: 'L')
extracted : "HE"  (2 bytes)
```

## Demo hai VM

```bash
# VM A (sender) — IP ví dụ 192.168.1.100
sudo insmod steg_net.ko peer_ip=192.168.1.200 'secret="Secret message"'
nc 192.168.1.200 8080    # gửi TCP → mỗi gói mang 1 ký tự ẩn

# VM B (receiver) — IP ví dụ 192.168.1.200
sudo insmod steg_net.ko peer_ip=192.168.1.100
nc -l 8080               # nhận TCP → dmesg hiển thị từng ký tự trích xuất
```

## Kiến thức áp dụng

- **Netfilter**: `struct nf_hook_ops`, `nf_register_net_hook()`, `NF_ACCEPT`
- **sk_buff**: `ip_hdr()` truy cập IP header, đọc/ghi trường `id`
- **IP checksum**: `ip_fast_csum()` tính lại sau khi sửa header
- **atomic_t**: đếm `embed_pos` an toàn khi hook chạy concurrent
- **spinlock**: bảo vệ buffer `extracted` (hook chạy trong softirq context)
- **/proc**: `proc_create()` + `seq_file` để hiển thị trạng thái

## Lưu ý

- **Snapshot VMware trước khi `insmod`** — lỗi kernel có thể panic máy ảo.
- Luôn `sudo rmmod steg_net` trước khi sửa code và build lại.
- API nhân có thể thay đổi theo phiên bản. Code này dùng API kernel **≥ 5.6**
  (`proc_ops` thay `file_operations` cho `/proc`). Test trên Ubuntu 22.04 / kernel 5.15.
- File tạo trên Windows bị dính `\r`: chạy `dos2unix *.c Makefile` trước khi build.
