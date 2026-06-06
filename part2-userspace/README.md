# Phần 2 — Lập trình user-space

Quản lý tiến trình, file, và socket/network trong Ubuntu (C, POSIX/syscall).

| File | Chức năng |
|---|---|
| `proc_info.c` | Liệt kê tiến trình đang chạy (đọc `/proc`) |
| `file_ops.c`  | Tạo/ghi/đọc file + xem thông tin (`open/read/write/stat`) |
| `tcp_server.c`| Socket server TCP, echo dữ liệu |
| `tcp_client.c`| Socket client TCP |

## Build

```bash
make            # biên dịch tất cả
make clean      # xóa file build
```

## Chạy thử socket (2 cửa sổ terminal)

```bash
# Cửa sổ 1
./tcp_server 60000

# Cửa sổ 2
./tcp_client 127.0.0.1 60000
# gõ tin nhắn -> server echo lại
```

```bash
./proc_info             # xem danh sách tiến trình
./file_ops test.txt     # demo thao tác file
```
