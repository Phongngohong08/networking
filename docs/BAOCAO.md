# Báo cáo cuối kỳ — Lập trình nhân Linux

**Đề tài 42:** Lập trình shell để quản lý file, lập lịch tác vụ, thiết lập thời gian hệ thống, cài đặt/gỡ bỏ các chương trình tự động; Lập trình quản lý tiến trình, file, socket và network trong Ubuntu; Lập trình xây dựng một mô-đun nhân và tích hợp vào hệ thống — **Networking**.

---

## LỜI MỞ ĐẦU

Nhân (kernel) là thành phần cốt lõi của hệ điều hành, chịu trách nhiệm quản lý tài nguyên phần cứng, tiến trình, bộ nhớ và đặc biệt là toàn bộ hoạt động truyền thông mạng. Trong khi lập trình ứng dụng thông thường chỉ làm việc ở không gian người dùng (user space) thông qua các lời gọi hệ thống, thì lập trình ở mức nhân cho phép can thiệp trực tiếp vào luồng xử lý gói tin, giám sát và điều khiển mạng ở mức sâu nhất mà các công cụ user-space không thể tiếp cận.

Đề tài của nhóm tập trung vào chủ đề **Networking** trong nhân Linux: xây dựng các mô-đun nhân (kernel module) có khả năng bắt giữ, phân tích và lọc gói tin bằng cơ chế **Netfilter**, cũng như tạo socket và truyền/nhận dữ liệu ngay trong không gian nhân. Bên cạnh đó, nhóm cũng triển khai các phần bổ trợ về lập trình shell và lập trình user-space để minh họa bức tranh tổng thể từ tầng ứng dụng xuống tầng nhân.

Trong quá trình thực hiện không tránh khỏi thiếu sót, nhóm rất mong nhận được sự góp ý của thầy/cô để hoàn thiện hơn. Nhóm xin chân thành cảm ơn!

---

## CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

### 1.1 Giới thiệu đề tài

Đề tài được chia thành ba phần với phần trọng tâm là lập trình mạng ở mức nhân:

1. **Lập trình shell**: quản lý file, lập lịch tác vụ, thiết lập thời gian hệ thống, cài đặt/gỡ bỏ chương trình tự động.
2. **Lập trình user-space**: quản lý tiến trình, file, socket và network trong Ubuntu.
3. **Lập trình kernel module — Networking** *(trọng tâm)*: xây dựng mô-đun nhân thực hiện các tác vụ mạng (giám sát, lọc gói tin, socket trong nhân) và tích hợp vào hệ thống.

### 1.2 Mục tiêu

- Hiểu kiến trúc tầng mạng (network stack) của nhân Linux và đường đi của một gói tin.
- Nắm vững cơ chế **Netfilter hook** để chặn/giám sát gói tin tại các điểm khác nhau trong stack.
- Biết cách đọc thông tin gói tin qua cấu trúc `sk_buff` (IP, TCP, UDP header).
- Lập trình socket **trong không gian nhân**: tạo socket, lắng nghe, nhận và gửi dữ liệu.
- Giao tiếp giữa user-space và kernel thông qua cơ chế **ioctl**.
- Tích hợp, nạp/gỡ mô-đun vào hệ thống đang chạy và kiểm thử kết quả.

### 1.3 Môi trường thực hiện

| Thành phần | Giá trị |
|---|---|
| Hệ điều hành | Ubuntu Server (kernel 5.15.0-179-generic) |
| Ảo hóa | VMware / VirtualBox |
| Trình biên dịch | gcc, make |
| Gói phụ thuộc | build-essential, linux-headers-$(uname -r) |
| Ngôn ngữ | C (kernel & user-space), Bash (shell), Python/Flask (demo) |

---

## CHƯƠNG 2. CƠ SỞ LÝ THUYẾT

### 2.1 Kiến trúc tầng mạng trong nhân Linux

Khi một gói tin đi vào hoặc đi ra khỏi máy, nó phải đi qua một chuỗi xử lý trong nhân Linux gọi là *network stack*. Stack này được tổ chức theo mô hình phân tầng (tương ứng mô hình TCP/IP): tầng liên kết (link), tầng mạng (IP), tầng giao vận (TCP/UDP) và cuối cùng được chuyển lên cho ứng dụng ở user-space thông qua socket.

Điểm mấu chốt là toàn bộ gói tin — kể cả lưu lượng localhost — đều đi qua nhân. Vì vậy, can thiệp ở mức nhân cho phép quan sát và điều khiển mạng một cách toàn diện.

### 2.2 Cấu trúc `struct sk_buff`

`sk_buff` (socket buffer) là cấu trúc trung tâm biểu diễn một gói tin trong nhân Linux. Mỗi gói tin khi đi qua stack đều được đóng gói trong một `sk_buff` chứa dữ liệu gói cùng các con trỏ tới từng tầng header. Nhân cung cấp các hàm trợ giúp để truy cập header:

- `ip_hdr(skb)` — trả về con trỏ tới IP header (`struct iphdr`).
- `tcp_hdr(skb)` — trả về con trỏ tới TCP header (`struct tcphdr`).
- `udp_hdr(skb)` — trả về con trỏ tới UDP header (`struct udphdr`).

Từ các header này ta đọc được địa chỉ nguồn/đích (`saddr`, `daddr`), cổng (`source`, `dest`), giao thức (`protocol`) và các cờ điều khiển (SYN, ACK, FIN...).

### 2.3 `struct socket` và `struct sock`

- `struct socket`: lớp trừu tượng BSD socket ở phía giao tiếp, chứa trường `ops` (các thao tác theo giao thức) và `sk` (liên kết tới socket INET nội bộ).
- `struct sock`: biểu diễn nội bộ của một socket INET, lưu trạng thái kết nối, thông tin giao thức và các hàm callback khi có sự kiện (dữ liệu đến, đổi trạng thái...).

### 2.4 Netfilter và các điểm hook

**Netfilter** là khung (framework) cho phép đăng ký các hàm callback (*hook*) vào những vị trí cố định trên đường đi của gói tin. Đây là nền tảng của `iptables`/`nftables`. Một hook được mô tả bằng `struct nf_hook_ops` và đăng ký qua `nf_register_net_hook()`.

Các điểm hook chính cho IPv4:

| Hook | Vị trí | Dùng để |
|---|---|---|
| `NF_INET_PRE_ROUTING` | Ngay khi gói vừa vào, trước định tuyến | Lọc/giám sát gói **đến** |
| `NF_INET_LOCAL_IN` | Gói đến tiến trình cục bộ | Firewall inbound |
| `NF_INET_FORWARD` | Gói được chuyển tiếp | Router/NAT |
| `NF_INET_LOCAL_OUT` | Gói do chính máy tạo ra, đi ra | Lọc/giám sát gói **đi** |
| `NF_INET_POST_ROUTING` | Trước khi gói rời máy | NAT nguồn |

Hàm hook trả về giá trị quyết định số phận gói tin, phổ biến nhất là:

- `NF_ACCEPT` — cho gói đi tiếp.
- `NF_DROP` — loại bỏ gói tin.

### 2.5 Lập trình socket trong không gian nhân

Nhân cung cấp API để tạo và thao tác socket ngay trong kernel, song song với API user-space:

- `sock_create_kern()` — tạo socket trong nhân.
- `kernel_bind()`, `kernel_listen()`, `kernel_accept()` — tương ứng với `bind/listen/accept`.
- `kernel_sendmsg()`, `kernel_recvmsg()` — gửi/nhận dữ liệu, dùng cùng `struct msghdr` và `struct kvec`.

### 2.6 Cơ sở các phần bổ trợ

- **Shell scripting**: ngôn ngữ kịch bản của Bash, thao tác hệ thống qua các lệnh (`crontab`, `at`, `timedatectl`, `apt`).
- **Lập trình user-space**: sử dụng các lời gọi hệ thống POSIX (`socket`, `open`, `read`, `/proc`) để quản lý tiến trình, file và mạng.
- **Kernel module & ioctl**: cơ chế nạp mã vào nhân lúc chạy (`insmod`/`rmmod`) và kênh giao tiếp user↔kernel qua `ioctl` trên thiết bị ký tự.

---

## CHƯƠNG 3. PHÂN TÍCH, THIẾT KẾ VÀ TRIỂN KHAI

### 3.1 Tổng quan kiến trúc dự án

Dự án được tổ chức thành bốn phần độc lập:

```
networking/
├── part1-shell/          # Phần 1: shell scripts
├── part2-userspace/      # Phần 2: chương trình C user-space
├── part3-kernel-module/  # Phần 3: kernel module networking (TRỌNG TÂM)
└── part4-web/            # Phần 4: web dashboard demo (bổ trợ)
```

### 3.2 Phần 1 — Lập trình shell (tóm tắt)

Gồm bốn script Bash:

| Script | Chức năng |
|---|---|
| `file_manager.sh` | Menu quản lý file/thư mục: liệt kê, tạo, xóa, tìm, sao lưu (tar.gz) |
| `scheduler.sh` | Lập lịch tác vụ bằng `cron` và `at` |
| `set_time.sh` | Xem/thiết lập thời gian, đồng bộ NTP, đổi múi giờ qua `timedatectl` |
| `pkg_manager.sh` | Cài đặt/gỡ bỏ chương trình tự động qua `apt`, hỗ trợ cài hàng loạt từ file |

### 3.3 Phần 2 — Lập trình user-space (tóm tắt)

Gồm các chương trình C minh họa quản lý tiến trình, file và socket:

| Chương trình | Chức năng |
|---|---|
| `proc_info.c` | Liệt kê tiến trình đang chạy bằng cách đọc thư mục `/proc` |
| `file_ops.c` | Tạo/ghi/đọc file và xem thông tin file qua syscall (`open/read/write/stat`) |
| `tcp_server.c` | Socket server TCP, nhận và echo dữ liệu từ client |
| `tcp_client.c` | Socket client TCP kết nối tới server |

### 3.4 Phần 3 — Kernel module Networking (TRỌNG TÂM)

Phần này triển khai đầy đủ năm bài thực hành của Linux Kernel Labs về networking, mỗi bài là một mô-đun nhân độc lập.

#### 3.4.1 Bài 1 — Giám sát gói tin (`net_monitor.c`)

Mô-đun đăng ký một Netfilter hook tại `NF_INET_PRE_ROUTING` để bắt mọi gói tin đến. Với mỗi gói IP, mô-đun đọc header và in ra nhật ký nhân (dmesg): giao thức, địa chỉ nguồn → đích, cổng và cờ TCP.

Đoạn mã cốt lõi của hàm hook:

```c
static unsigned int hook_func(void *priv, struct sk_buff *skb,
                              const struct nf_hook_state *state)
{
    struct iphdr *iph = ip_hdr(skb);
    if (!iph) return NF_ACCEPT;

    switch (iph->protocol) {
    case IPPROTO_TCP: {
        struct tcphdr *tcph = tcp_hdr(skb);
        pr_info("net_monitor: TCP %pI4:%u -> %pI4:%u [%s%s%s]\n",
                &iph->saddr, ntohs(tcph->source),
                &iph->daddr, ntohs(tcph->dest),
                tcph->syn ? "SYN " : "", tcph->ack ? "ACK " : "",
                tcph->fin ? "FIN " : "");
        break;
    }
    /* ... UDP, ICMP tương tự ... */
    }
    return NF_ACCEPT;   /* chỉ giám sát, không chặn */
}
```

Đăng ký hook trong hàm init:

```c
nfho.hook     = hook_func;
nfho.hooknum  = NF_INET_PRE_ROUTING;
nfho.pf       = PF_INET;
nfho.priority = NF_IP_PRI_FIRST;
nf_register_net_hook(&init_net, &nfho);
```

#### 3.4.2 Bài 2 — Lọc gói tin theo địa chỉ đích (`net_filter.c` + `filter_ctl.c`)

Mô-đun chặn (DROP) các gói tin có địa chỉ IP đích trùng với giá trị được cấu hình động. Việc cấu hình được thực hiện từ user-space thông qua **ioctl**: mô-đun tạo thiết bị ký tự `/dev/netfilter_ctl`, công cụ `filter_ctl` gửi địa chỉ IP cần chặn xuống nhân.

Điểm quan trọng về kỹ thuật: vì mục tiêu là chặn gói **đi ra** từ máy (ví dụ `ping` tới một IP), hook phải đặt tại `NF_INET_LOCAL_OUT` chứ không phải `PRE_ROUTING`. Lý do: gói `ping` đi ra có `daddr` là IP cần chặn, trong khi gói phản hồi đi vào lại có `daddr` là IP của chính máy ta — nếu hook ở `PRE_ROUTING` sẽ không khớp và không chặn được.

```c
static unsigned int hook_func(void *priv, struct sk_buff *skb,
                              const struct nf_hook_state *state)
{
    struct iphdr *iph;
    if (!skb || blocked_addr == 0) return NF_ACCEPT;

    iph = ip_hdr(skb);
    if (iph && iph->daddr == blocked_addr) {
        pr_info("net_filter: DROP goi den %pI4\n", &iph->daddr);
        return NF_DROP;
    }
    return NF_ACCEPT;
}
```

Xử lý ioctl để nhận IP từ user-space:

```c
static long ctl_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
    __be32 addr;
    switch (cmd) {
    case FILTER_SET_ADDR:
        if (copy_from_user(&addr, (void __user *)arg, sizeof(addr)))
            return -EFAULT;
        blocked_addr = addr;
        break;
    case FILTER_CLR_ADDR:
        blocked_addr = 0;
        break;
    default:
        return -ENOTTY;
    }
    return 0;
}
```

#### 3.4.3 Bài 3 + 4 — TCP listen/accept trong nhân (`ksock_tcp.c`)

Mô-đun tạo một socket TCP **ngay trong nhân**, bind và lắng nghe tại cổng 60000, sau đó chấp nhận kết nối và đọc dữ liệu client gửi. Toàn bộ chạy trong một *kernel thread* để không chặn quá trình nạp mô-đun.

```c
sock_create_kern(&init_net, AF_INET, SOCK_STREAM, IPPROTO_TCP, &listen_sock);

addr.sin_family      = AF_INET;
addr.sin_addr.s_addr = htonl(INADDR_ANY);
addr.sin_port        = htons(60000);

kernel_bind(listen_sock, (struct sockaddr *)&addr, sizeof(addr));
kernel_listen(listen_sock, 5);

while (!kthread_should_stop()) {
    ret = kernel_accept(listen_sock, &conn, O_NONBLOCK);
    if (ret == -EAGAIN) { msleep(200); continue; }
    if (ret == 0) {
        kernel_recvmsg(conn, &msg, &vec, 1, BUFSZ - 1, 0);  /* đọc dữ liệu */
        sock_release(conn);
    }
}
```

Việc dùng `kernel_accept` ở chế độ không chặn (`O_NONBLOCK`) kết hợp `msleep` giúp `rmmod` gỡ mô-đun sạch sẽ (nếu accept chặn vô hạn sẽ làm treo `kthread_stop`).

#### 3.4.4 Bài 5 — Gửi UDP từ nhân (`ksock_udp.c`)

Mô-đun tạo socket UDP trong nhân và gửi một thông điệp tới địa chỉ/cổng đích (truyền qua tham số mô-đun). Sử dụng `kernel_sendmsg` với `struct msghdr` và `struct kvec`.

```c
sock_create_kern(&init_net, AF_INET, SOCK_DGRAM, IPPROTO_UDP, &sock);

addr.sin_family      = AF_INET;
addr.sin_port        = htons(dport);
addr.sin_addr.s_addr = in_aton(dip);

mhdr.msg_name    = &addr;
mhdr.msg_namelen = sizeof(addr);
vec.iov_base     = msg;
vec.iov_len      = strlen(msg);

kernel_sendmsg(sock, &mhdr, &vec, 1, vec.iov_len);
sock_release(sock);
```

### 3.5 Phần 4 — Web dashboard (bổ trợ)

Để demo trực quan, nhóm xây dựng một bảng điều khiển web tối giản bằng Flask. Backend chạy trên chính máy Ubuntu, đóng vai trò cầu nối giữa trình duyệt và hệ thống: nạp/gỡ mô-đun, **stream nhật ký dmesg theo thời gian thực**, cấu hình lọc IP. Tên mô-đun được kiểm soát bằng whitelist và địa chỉ IP được kiểm tra hợp lệ nhằm bảo đảm an toàn.

---

## CHƯƠNG 4. KẾT QUẢ THỰC NGHIỆM

### 4.1 Biên dịch

Biên dịch toàn bộ mô-đun và công cụ bằng lệnh `make` trong thư mục `part3-kernel-module`. Kết quả tạo ra bốn tệp `.ko` (`net_monitor.ko`, `net_filter.ko`, `ksock_tcp.ko`, `ksock_udp.ko`) và công cụ `filter_ctl`. Cảnh báo *"Skipping BTF generation"* là vô hại (chỉ liên quan tới thông tin gỡ lỗi BTF), không ảnh hưởng tới hoạt động của mô-đun.

*[Hình 4.1 — Ảnh chụp kết quả biên dịch `make` thành công]*

### 4.2 Kết quả từng bài

**Bài 1 — Giám sát gói tin.** Sau khi nạp `net_monitor.ko` và theo dõi `dmesg -w`, mô-đun bắt được mọi gói tin đi qua máy. Ví dụ một lát cắt nhật ký thực tế:

```
net_monitor: TCP 192.168.0.102:53270 -> 192.168.0.108:22 [ACK ]
net_monitor: ICMP 8.8.8.8 -> 192.168.0.105
net_monitor: UDP 127.0.0.1:35681 -> 127.0.0.53:53
net_monitor: UDP 8.8.8.8:53 -> 192.168.0.105:55135
```

Phân tích: dòng TCP tới cổng 22 là phiên SSH đang điều khiển máy ảo; dòng UDP tới `127.0.0.53:53` là truy vấn DNS qua systemd-resolved; dòng UDP từ `8.8.8.8:53` là phản hồi DNS của Google; dòng ICMP là gói trả lời ping. Kết quả cho thấy mô-đun bắt được cả lưu lượng localhost lẫn lưu lượng ra ngoài.

*[Hình 4.2 — Nhật ký dmesg của net_monitor]*

**Bài 2 — Lọc theo IP đích.** Nạp `net_filter.ko`, dùng `filter_ctl set 8.8.8.8` rồi `ping 8.8.8.8` cho kết quả 100% packet loss; nhật ký dmesg hiển thị các dòng "DROP goi den 8.8.8.8". Sau khi `filter_ctl clear`, ping hoạt động trở lại bình thường.

*[Hình 4.3 — Kết quả chặn gói: ping bị 100% packet loss và log DROP]*

**Bài 3 + 4 — TCP trong nhân.** Nạp `ksock_tcp.ko`, từ một terminal khác chạy `echo "hello kernel" | nc 127.0.0.1 60000`; nhật ký dmesg hiển thị dữ liệu nhận được, chứng tỏ socket nhân đã lắng nghe và đọc dữ liệu thành công.

*[Hình 4.4 — dmesg hiển thị dữ liệu nhận được từ kết nối TCP]*

**Bài 5 — Gửi UDP từ nhân.** Mở listener `nc -u -l 5005`, sau đó nạp mô-đun:

```
sudo insmod ksock_udp.ko dip="127.0.0.1" dport=5005 'msg="Xin chao tu kernel"'
```

Lưu ý: tham số `msg` chứa khoảng trắng nên phải bọc trong dấu nháy đơn bao quanh cả `key="value"` để dấu nháy kép được truyền nguyên vẹn xuống nhân (vì `insmod` ghép các tham số bằng dấu cách rồi nhân mới tách lại). Kết quả listener nhận được đúng chuỗi gửi từ nhân.

*[Hình 4.5 — Listener nhận được thông điệp UDP gửi từ kernel]*

### 4.3 Đánh giá

| Bài | Yêu cầu | Kết quả |
|---|---|---|
| 1 | Giám sát/hiển thị gói tin | Đạt |
| 2 | Lọc gói theo IP đích (ioctl) | Đạt |
| 3 | TCP listen trong nhân | Đạt |
| 4 | Accept kết nối trong nhân | Đạt |
| 5 | Gửi UDP từ nhân | Đạt |

Các mô-đun nạp/gỡ ổn định, không gây lỗi nhân. Web dashboard hoạt động đúng, hỗ trợ demo trực quan.

---

## KẾT LUẬN

Nhóm đã hoàn thành đề tài với trọng tâm là lập trình mạng ở mức nhân Linux: nắm được kiến trúc network stack, cơ chế Netfilter, cách đọc gói tin qua `sk_buff` và lập trình socket trong không gian nhân. Năm bài thực hành networking đều được triển khai thành mô-đun độc lập, biên dịch và chạy thành công trên Ubuntu kernel 5.15. Các phần bổ trợ về shell và user-space giúp hoàn thiện bức tranh tổng thể từ tầng ứng dụng xuống tầng nhân, kèm một web dashboard hỗ trợ demo.

**Hướng phát triển:** mở rộng bộ lọc theo cả cổng và giao thức, hỗ trợ IPv6, thống kê lưu lượng theo thời gian thực, và bổ sung cơ chế xác thực cho web dashboard để có thể dùng an toàn ngoài môi trường demo.

---

## TÀI LIỆU THAM KHẢO

1. Linux Kernel Labs — *Networking*. https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html
2. Robert Love, *Linux Kernel Development*, 3rd Edition, Addison-Wesley.
3. The Linux Kernel Documentation — *Netfilter*. https://www.kernel.org/doc/html/latest/networking/
4. Tài liệu mã nguồn nhân Linux: `include/linux/skbuff.h`, `include/linux/netfilter.h`, `net/socket.c`.
