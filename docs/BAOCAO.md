# Báo cáo cuối kỳ — Lập trình nhân Linux

**Đề tài 42:** Lập trình shell để quản lý file, lập lịch tác vụ, thiết lập thời gian hệ thống, cài đặt/gỡ bỏ các chương trình tự động; Lập trình quản lý tiến trình, file, socket và network trong Ubuntu; Xây dựng mô-đun nhân **giấu tin trong gói TCP/UDP** và tích hợp vào hệ thống.

---

## LỜI MỞ ĐẦU

Nhân Linux (Linux Kernel) là thành phần cốt lõi của hệ điều hành, chịu trách nhiệm quản lý tài nguyên phần cứng, tiến trình, bộ nhớ và toàn bộ hoạt động mạng. Lập trình ở mức nhân cho phép can thiệp trực tiếp vào luồng xử lý gói tin — điều mà các chương trình user-space không thể thực hiện được.

Đề tài của nhóm gồm ba phần: lập trình shell tự động hoá tác vụ hệ thống, lập trình C user-space quản lý tiến trình và mạng, và phần trọng tâm là xây dựng mô-đun nhân thực hiện kỹ thuật **giấu tin trong gói TCP** (network steganography) — một ứng dụng thực tế của lập trình mạng ở mức nhân.

Nhóm xin chân thành cảm ơn thầy/cô đã hướng dẫn trong quá trình thực hiện đề tài!

---

## CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

### 1.1 Giới thiệu

Đề tài 42 bao gồm ba phần:

1. **Lập trình shell** — viết script Bash tự động hoá quản lý file, lập lịch tác vụ, thiết lập thời gian và quản lý gói phần mềm.
2. **Lập trình C user-space** — quản lý tiến trình, thao tác file hệ thống và lập trình socket TCP/UDP trong Ubuntu.
3. **Xây dựng mô-đun nhân** *(trọng tâm)* — module `steg_net` giấu thông điệp bí mật trong trường **IP Identification** của gói TCP sử dụng framework Netfilter.

### 1.2 Mục tiêu

- Thành thạo lập trình Bash, bao gồm xử lý file, cron/at, timedatectl và apt.
- Sử dụng syscall POSIX để quản lý tiến trình, file và socket trong C.
- Hiểu cấu trúc module nhân Linux: `module_init/exit`, `MODULE_LICENSE`, nạp/gỡ mô-đun.
- Nắm vững framework **Netfilter**: đăng ký hook, đọc gói tin qua `struct sk_buff`.
- Triển khai kỹ thuật **steganography mạng**: nhúng và trích xuất dữ liệu ẩn trong header gói tin.

### 1.3 Môi trường thực hiện

| Thành phần | Giá trị |
|---|---|
| Hệ điều hành | Ubuntu Server 22.04 (kernel 5.15.0-generic) |
| Ảo hóa | VMware Workstation / VirtualBox |
| Trình biên dịch | gcc 11, make |
| Gói phụ thuộc | `build-essential`, `linux-headers-$(uname -r)` |
| Ngôn ngữ | C (nhân & user-space), Bash |

---

## CHƯƠNG 2. LẬP TRÌNH SHELL

### 2.1 Tổng quan

Phần này gồm bốn script Bash, mỗi script thực hiện một nhóm chức năng quản trị hệ thống:

| Script | Chức năng chính |
|---|---|
| `file_manager.sh` | Quản lý file/thư mục: liệt kê, tạo, xóa, tìm kiếm, sao lưu nén `.tar.gz` |
| `scheduler.sh` | Lập lịch tác vụ định kỳ bằng `cron`, tác vụ một lần bằng `at` |
| `set_time.sh` | Xem/thiết lập ngày giờ hệ thống, đổi múi giờ, đồng bộ NTP qua `timedatectl` |
| `pkg_manager.sh` | Cài đặt/gỡ bỏ phần mềm qua `apt`, hỗ trợ cài hàng loạt từ danh sách file |

### 2.2 Quản lý file — `file_manager.sh`

Script sử dụng menu dạng `select` để người dùng chọn thao tác. Tính năng sao lưu dùng `tar -czf` để nén thư mục, kết hợp timestamp vào tên file để tránh ghi đè:

```bash
backup_dir() {
    local target="$1"
    local dest="backup_$(basename "$target")_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$dest" "$target" && echo "Da sao luu: $dest"
}
```

### 2.3 Lập lịch tác vụ — `scheduler.sh`

Script hỗ trợ hai cơ chế lập lịch của Linux:
- **cron**: thêm/xóa/liệt kê crontab với cú pháp `cron expression` (phút, giờ, ngày, tháng, thứ).
- **at**: thực thi một lần tại thời điểm cụ thể, ví dụ `echo "cleanup.sh" | at 02:00`.

### 2.4 Thiết lập thời gian — `set_time.sh`

Sử dụng `timedatectl` — công cụ hệ thống của systemd để quản lý thời gian. Script cho phép bật/tắt đồng bộ NTP, đổi múi giờ và xem trạng thái thời gian hiện tại:

```bash
timedatectl set-timezone Asia/Ho_Chi_Minh
timedatectl set-ntp true
timedatectl status
```

### 2.5 Quản lý gói — `pkg_manager.sh`

Script bọc lại `apt-get` để cung cấp giao diện thân thiện hơn, hỗ trợ:
- Cài/gỡ từng gói với kiểm tra quyền root.
- Cài hàng loạt từ file danh sách (`packages.txt`), mỗi dòng một tên gói.
- Hiển thị danh sách gói đã cài và trạng thái.

*[Hình 2.1 — Minh họa chạy file_manager.sh và scheduler.sh]*

---

## CHƯƠNG 3. LẬP TRÌNH C TRONG LINUX

### 3.1 Tổng quan

Phần này gồm bốn chương trình C minh hoạ các thao tác cốt lõi ở user-space:

| Chương trình | Mô tả |
|---|---|
| `proc_info.c` | Liệt kê tiến trình đang chạy bằng cách duyệt thư mục `/proc` |
| `file_ops.c` | Tạo, ghi, đọc file và xem thông tin qua syscall POSIX |
| `tcp_server.c` | TCP server: lắng nghe, nhận kết nối, echo dữ liệu về client |
| `tcp_client.c` | TCP client: kết nối tới server và gửi dữ liệu |

### 3.2 Quản lý tiến trình — `proc_info.c`

Thay vì dùng lệnh `ps`, chương trình đọc trực tiếp từ hệ thống file ảo `/proc`. Mỗi thư mục con có tên là số nguyên trong `/proc` tương ứng với một PID đang chạy. File `/proc/<pid>/status` chứa tên tiến trình, trạng thái và thông tin bộ nhớ:

```c
DIR *dp = opendir("/proc");
while ((entry = readdir(dp)) != NULL) {
    if (!isdigit(entry->d_name[0])) continue;   /* chỉ lấy thư mục PID */
    snprintf(path, sizeof(path), "/proc/%s/status", entry->d_name);
    /* đọc và in Name, State, VmRSS từ file status */
}
```

### 3.3 Thao tác file — `file_ops.c`

Minh hoạ bốn syscall cơ bản của POSIX:
- `open()` — mở/tạo file với flag (`O_CREAT`, `O_WRONLY`, `O_RDONLY`).
- `write()` / `read()` — ghi và đọc dữ liệu nhị phân.
- `stat()` — lấy thông tin file (kích thước, thời gian, quyền truy cập).
- `close()` — đóng file descriptor.

### 3.4 Lập trình socket TCP — `tcp_server.c` và `tcp_client.c`

Server tạo socket, bind cổng, listen và vòng lặp accept để phục vụ nhiều client:

```c
int sfd = socket(AF_INET, SOCK_STREAM, 0);
setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
bind(sfd, (struct sockaddr *)&addr, sizeof(addr));
listen(sfd, 5);

while (1) {
    int cfd = accept(sfd, NULL, NULL);
    recv(cfd, buf, sizeof(buf), 0);
    send(cfd, buf, strlen(buf), 0);   /* echo */
    close(cfd);
}
```

Client kết nối và gửi chuỗi do người dùng nhập, sau đó nhận và in phản hồi từ server.

*[Hình 3.1 — Chạy tcp_server và tcp_client trong hai terminal]*

---

## CHƯƠNG 4. MODULE NHÂN — GIẤU TIN TRONG GÓI TCP

### 4.1 Đặt vấn đề

**Steganography** (kỹ thuật giấu tin) là phương pháp ẩn thông điệp trong một vật chứa (carrier) sao cho người ngoài không nhận ra sự tồn tại của thông tin ẩn. Khác với mã hóa (biến nội dung thành không đọc được), steganography **giữ nguyên bề ngoài** của dữ liệu truyền đi.

**Steganography mạng** (network steganography) sử dụng các trường ít dùng hoặc dư thừa trong header gói tin để mang dữ liệu ẩn. Các vật chứa phổ biến:
- Trường **IP Identification** (16-bit) — dùng để tái hợp phân mảnh, thường là số ngẫu nhiên.
- Các bit dự phòng trong TCP header (Reserved bits).
- Trường **IP TTL** — giá trị giảm dần, có thể mã hóa thông tin theo quy luật thay đổi.
- **Timing covert channel** — mã hóa bit qua khoảng cách thời gian giữa các gói.

Module `steg_net` sử dụng trường **IP Identification** vì:
1. 16-bit đủ để mang 1 byte ký tự + 1 byte magic marker.
2. Hầu hết kernel hiện đại đặt IP ID = giá trị ngẫu nhiên cho từng gói — thay thế nó không gây phân mảnh.
3. Kỹ thuật đọc/ghi đơn giản, không ảnh hưởng định tuyến hay TCP handshake.

### 4.2 Cơ sở lý thuyết

#### 4.2.1 Module nhân Linux (LKM)

**Loadable Kernel Module** là đoạn mã chạy trong không gian nhân (kernel space — ring 0), có thể nạp vào nhân đang chạy mà không cần khởi động lại hệ thống. Module phải khai báo hai hàm:

```c
module_init(ten_ham_init);   /* gọi khi insmod */
module_exit(ten_ham_exit);   /* gọi khi rmmod  */
MODULE_LICENSE("GPL");
```

Biên dịch module dùng hệ thống build của nhân (`kbuild`) với `obj-m` trong Makefile:

```makefile
obj-m += steg_net.o
$(MAKE) -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
```

Nạp và gỡ module:

```bash
sudo insmod steg_net.ko peer_ip=127.0.0.1 'secret="HELLO"'
sudo rmmod steg_net
dmesg | grep steg   # xem log từ module
```

#### 4.2.2 Kiến trúc tầng mạng trong nhân Linux

Khi một gói tin đi qua hệ thống, nó được biểu diễn bằng cấu trúc `struct sk_buff` (socket buffer) — "gói bọc" trung tâm chứa con trỏ tới từng tầng header:

- `ip_hdr(skb)` → `struct iphdr` — IP header (giao thức, địa chỉ nguồn/đích, IP ID).
- `tcp_hdr(skb)` → `struct tcphdr` — TCP header (cổng, cờ SYN/ACK/FIN).
- `udp_hdr(skb)` → `struct udphdr` — UDP header (cổng nguồn/đích).

Toàn bộ lưu lượng mạng — kể cả localhost — đều đi qua nhân và có thể bị bắt/sửa tại đây.

#### 4.2.3 Framework Netfilter

**Netfilter** cho phép đăng ký hàm callback (hook) vào các điểm cố định trên đường đi của gói tin. Đây là nền tảng của `iptables`. Các điểm hook IPv4 chính:

| Hook | Vị trí | Ứng dụng |
|---|---|---|
| `NF_INET_PRE_ROUTING` | Trước khi định tuyến | Bắt gói **đến** từ mạng |
| `NF_INET_LOCAL_OUT` | Gói do máy tạo ra, đi ra | Bắt gói **đi** từ máy |
| `NF_INET_POST_ROUTING` | Sau định tuyến, sắp rời máy | NAT nguồn |

Đăng ký hook bằng `struct nf_hook_ops` và `nf_register_net_hook()`:

```c
static struct nf_hook_ops my_ops = {
    .hook    = my_hook_fn,
    .pf      = PF_INET,
    .hooknum = NF_INET_PRE_ROUTING,
    .priority = NF_IP_PRI_FIRST,
};
nf_register_net_hook(&init_net, &my_ops);
```

Hàm hook trả về `NF_ACCEPT` (cho gói đi tiếp) hoặc `NF_DROP` (hủy gói).

#### 4.2.4 Trường IP Identification

Theo RFC 791, trường **IP ID** (16-bit) dùng để tái hợp các phân mảnh IP: các mảnh của cùng một gói có cùng IP ID. Đối với gói không bị phân mảnh (phổ biến trong mạng LAN và loopback), giá trị IP ID không mang ý nghĩa đặc biệt — nhân Linux gán giá trị ngẫu nhiên. Vì vậy, thay thế IP ID bằng một giá trị có cấu trúc là vô hại và không thể phân biệt bằng quan sát bề ngoài.

### 4.3 Thiết kế module `steg_net`

#### 4.3.1 Kỹ thuật giấu tin

Module mã hóa mỗi ký tự của `secret` vào trường IP ID như sau:

```
IP_ID (16 bit):
┌────────────────┬──────────────────┐
│ Byte cao 0xAB  │  Byte thấp = ký tự │
│ (magic marker) │  secret[pos]       │
└────────────────┴──────────────────┘
   Ví dụ: secret="HELLO", gói đầu → IP_ID = 0xAB48 ('H' = 0x48)
```

- **Magic marker `0xAB`** ở byte cao giúp phía nhận nhận biết đây là "gói steg", phân biệt với lưu lượng TCP thông thường.
- Byte thấp chứa ký tự thứ `pos` của thông điệp, vị trí tăng dần theo từng gói.
- Khi hết thông điệp, pos quay vòng lại từ đầu.

Sau khi sửa IP ID, phải tính lại **IP checksum** để gói tin hợp lệ:

```c
iph->id    = htons(new_id);
iph->check = 0;
iph->check = ip_fast_csum((u8 *)iph, iph->ihl);
```

#### 4.3.2 Hai hook Netfilter

Module đăng ký hai hook:

| Hook | Điểm | Nhiệm vụ |
|---|---|---|
| `embed_hook` | `NF_INET_LOCAL_OUT` | Gói TCP ra ngoài tới `peer_ip` → nhúng ký tự vào IP ID |
| `extract_hook` | `NF_INET_PRE_ROUTING` | Gói TCP đến từ `peer_ip` → đọc IP ID, tái tạo thông điệp |

#### 4.3.3 Tham số module

```bash
sudo insmod steg_net.ko peer_ip=<địa_chỉ_IP> 'secret="<thông_điệp>"'
```

| Tham số | Mô tả | Mặc định |
|---|---|---|
| `peer_ip` | IP đích để nhúng tin / IP nguồn để trích tin (bắt buộc) | — |
| `secret` | Thông điệp cần giấu | `"Hello from kernel!"` |

#### 4.3.4 Theo dõi trạng thái qua `/proc`

Module tạo mục `/proc/steg_net` để xem trạng thái tức thời:

```bash
cat /proc/steg_net
# === steg_net status ===
# secret     : "HELLO"  (5 bytes)
# peer_ip    : 127.0.0.1
# magic      : 0xAB
# embed_pos  : 2  (ký tự tiếp theo: 'L')
# extracted  : "HE"  (2 bytes)
```

### 4.4 Triển khai — Mã nguồn chính

#### 4.4.1 Hàm EMBED

```c
static unsigned int embed_hook(void *priv, struct sk_buff *skb,
                               const struct nf_hook_state *state)
{
    struct iphdr *iph;
    int  pos;
    u16  new_id;

    if (!skb || !peer_addr) return NF_ACCEPT;
    iph = ip_hdr(skb);
    if (!iph || iph->protocol != IPPROTO_TCP) return NF_ACCEPT;
    if (iph->daddr != peer_addr) return NF_ACCEPT;

    /* Lấy ký tự tại vị trí hiện tại, tăng counter */
    pos    = atomic_inc_return(&embed_pos) - 1;
    pos    = pos % (int)secret_len;
    new_id = ((u16)STEG_MAGIC << 8) | (u8)secret[pos];

    /* Ghi vào IP ID và tính lại checksum */
    iph->id    = htons(new_id);
    iph->check = 0;
    iph->check = ip_fast_csum((u8 *)iph, iph->ihl);

    pr_info("steg [EMBED] pos=%d char='%c' IP_ID=0x%04X\n",
            pos, secret[pos], new_id);
    return NF_ACCEPT;
}
```

#### 4.4.2 Hàm EXTRACT

```c
static unsigned int extract_hook(void *priv, struct sk_buff *skb,
                                  const struct nf_hook_state *state)
{
    struct iphdr *iph;
    u16 ip_id;
    u8  magic, ch;

    if (!skb || !peer_addr) return NF_ACCEPT;
    iph = ip_hdr(skb);
    if (!iph || iph->protocol != IPPROTO_TCP) return NF_ACCEPT;
    if (iph->saddr != peer_addr) return NF_ACCEPT;

    ip_id = ntohs(iph->id);
    magic = (ip_id >> 8) & 0xFF;
    ch    =  ip_id       & 0xFF;

    if (magic != STEG_MAGIC) return NF_ACCEPT;   /* không phải gói steg */

    pr_info("steg [EXTRACT] IP_ID=0x%04X char='%c'\n", ip_id, ch);

    spin_lock(&extract_lock);
    if (extract_pos < EXTRACT_MAX - 1) {
        extracted[extract_pos++] = ch;
        extracted[extract_pos]   = '\0';
    }
    spin_unlock(&extract_lock);

    return NF_ACCEPT;
}
```

#### 4.4.3 Init và Exit

```c
static int __init steg_init(void)
{
    /* Kiểm tra tham số */
    if (!peer_ip || !*peer_ip) { pr_err("steg_net: thiếu peer_ip\n"); return -EINVAL; }
    if (in4_pton(peer_ip, -1, (u8 *)&peer_addr, -1, NULL) != 1) return -EINVAL;
    secret_len = strlen(secret);

    /* Đăng ký hai hook Netfilter */
    nf_register_net_hook(&init_net, &embed_ops);
    nf_register_net_hook(&init_net, &extract_ops);

    /* Tạo mục /proc/steg_net */
    proc_create("steg_net", 0444, NULL, &steg_proc_ops);

    pr_info("steg_net: nạp xong — secret=\"%s\" peer=%pI4\n", secret, &peer_addr);
    return 0;
}

static void __exit steg_exit(void)
{
    remove_proc_entry("steg_net", NULL);
    nf_unregister_net_hook(&init_net, &extract_ops);
    nf_unregister_net_hook(&init_net, &embed_ops);
    pr_info("steg_net: đã trích xuất được: \"%s\"\n", extracted);
}
```

### 4.5 Biên dịch và tích hợp vào nhân

**Cài đặt phụ thuộc:**

```bash
sudo apt update
sudo apt install build-essential linux-headers-$(uname -r)
```

**Biên dịch:**

```bash
cd part3-kernel-module
make
```

Kết quả tạo ra `steg_net.ko`. Cảnh báo *"Skipping BTF generation"* là vô hại (liên quan đến thông tin gỡ lỗi, không ảnh hưởng hoạt động module).

*[Hình 4.1 — Kết quả biên dịch `make` thành công, file steg_net.ko được tạo]*

**Nạp module:**

```bash
sudo insmod steg_net.ko peer_ip=127.0.0.1 'secret="HELLO"'
```

Kiểm tra module đã nạp:

```bash
lsmod | grep steg_net
```

**Gỡ module:**

```bash
sudo rmmod steg_net
```

### 4.6 Kết quả thực nghiệm

**Thiết lập demo (một VM, dùng loopback):**

```bash
# Terminal 1 — mở listener
nc -l 7777

# Terminal 2 — gửi dữ liệu TCP
echo "test data" | nc 127.0.0.1 7777
```

**Nhật ký kernel (dmesg):**

```
steg_net: nạp xong — secret="HELLO" peer=127.0.0.1
steg [EMBED] pos=0  char='H'(0x48)  IP_ID=0xAB48  -> 127.0.0.1
steg [EMBED] pos=1  char='E'(0x45)  IP_ID=0xAB45  -> 127.0.0.1
steg [EMBED] pos=2  char='L'(0x4C)  IP_ID=0xAB4C  -> 127.0.0.1
steg [EXTRACT] IP_ID=0xAB48  magic=0xAB  char='H'  from 127.0.0.1
steg [EXTRACT] IP_ID=0xAB45  magic=0xAB  char='E'  from 127.0.0.1
```

*[Hình 4.2 — Nhật ký dmesg hiển thị quá trình embed và extract]*

**Trạng thái /proc:**

```bash
cat /proc/steg_net
```

```
=== steg_net status ===
secret      : "HELLO"  (5 bytes)
peer_ip     : 127.0.0.1
magic       : 0xAB
embed_pos   : 3  (ký tự tiếp theo: 'L')
extracted   : "HEL"  (3 bytes)
```

*[Hình 4.3 — Nội dung /proc/steg_net]*

**Kết quả khi rmmod:**

```
steg_net: đã trích xuất được: "HELLO"
```

*[Hình 4.4 — Thông điệp trích xuất đầy đủ khi gỡ module]*

### 4.7 Đánh giá

| Yêu cầu | Kết quả |
|---|---|
| Xây dựng module nhân hợp lệ, nạp/gỡ ổn định | Đạt |
| Đăng ký hook Netfilter, bắt gói TCP | Đạt |
| Nhúng ký tự vào trường IP ID và tính lại checksum | Đạt |
| Trích xuất và tái tạo thông điệp từ gói đến | Đạt |
| Theo dõi trạng thái qua `/proc/steg_net` | Đạt |
| Không gây crash nhân, gỡ module sạch sẽ | Đạt |

---

## KẾT LUẬN

Nhóm đã hoàn thành đề tài với ba phần rõ ràng:

- **Phần 1 (Shell)**: bốn script Bash tự động hoá các tác vụ quản trị hệ thống thường gặp.
- **Phần 2 (C user-space)**: bốn chương trình minh hoạ quản lý tiến trình, file và lập trình socket TCP.
- **Phần 3 (Module nhân)**: module `steg_net` triển khai kỹ thuật giấu tin trong trường IP ID của gói TCP, sử dụng Netfilter hook — kết hợp lý thuyết mạng, lập trình nhân và bảo mật thông tin trong một demo trực quan.

Qua đề tài, nhóm đã nắm được vòng đời của module nhân, kiến trúc network stack, cách đọc/sửa header gói tin qua `struct sk_buff` và cơ chế Netfilter — những nền tảng quan trọng cho lập trình hệ thống ở mức thấp.

**Hướng phát triển:** mở rộng sang giấu tin trong TCP Sequence Number hoặc TTL để tăng băng thông kênh ẩn; triển khai mã hóa thông điệp trước khi giấu để tăng tính bảo mật; hỗ trợ IPv6.

---

## TÀI LIỆU THAM KHẢO

1. Linux Kernel Labs — *Networking*. https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html
2. Robert Love, *Linux Kernel Development*, 3rd Edition, Addison-Wesley, 2010.
3. The Linux Kernel Documentation — *Networking*. https://www.kernel.org/doc/html/latest/networking/
4. W. Mazurczyk, S. Wendzel, *Information Hiding in Communication Networks*, IEEE Press, 2016.
5. Mã nguồn nhân Linux: `include/linux/skbuff.h`, `include/linux/netfilter.h`, `net/socket.c`.
