# docs — Báo cáo & Thuyết trình

| File | Vai trò |
|---|---|
| `BAOCAO.md` | **Nguồn** báo cáo (Markdown) — commit lên git, dễ sửa/diff |
| `build_docx.py` | Script sinh file Word từ `BAOCAO.md` |
| `BaoCao_DeTai42_Networking.docx` | File Word để nộp — **gitignore**, sinh lại bằng script |
| `build_pptx.py` | Script sinh bài thuyết trình (22 slide) |
| `ThuyetTrinh_DeTai42_Networking.pptx` | Slide trình bày — **gitignore**, sinh lại bằng script |

## Sinh lại file Word / Slide

```bash
pip install python-docx python-pptx   # nếu chưa có

cd docs
python build_docx.py    # → BaoCao_DeTai42_Networking.docx
python build_pptx.py    # → ThuyetTrinh_DeTai42_Networking.pptx  (22 slide)
```

## Cấu trúc báo cáo (BAOCAO.md)

| Chương | Nội dung |
|---|---|
| Chương 1 | Tổng quan đề tài, mục tiêu, môi trường |
| Chương 2 | Lập trình Shell (4 script) |
| Chương 3 | Lập trình C user-space (4 chương trình) |
| Chương 4 | Module nhân `steg_net` — lý thuyết steganography, thiết kế, code, build, kết quả |
| Kết luận | Tổng kết + TÀI LIỆU THAM KHẢO |

## Cấu trúc thuyết trình (22 slide)

| Slide | Nội dung |
|---|---|
| 1 | Title |
| 2 | Agenda |
| 3 | Tổng quan đề tài |
| 4–8 | Kiến thức nền: Nhân Linux, kernel space, LKM, mạng, Netfilter |
| 9 | struct sk_buff |
| 10–11 | Steganography là gì? + kỹ thuật IP ID |
| 12 | Shell & C user-space (tóm tắt) |
| 13 | steg_net — thiết kế tổng quan |
| 14–15 | Code EMBED + EXTRACT |
| 16 | Init/Exit + /proc/steg_net |
| 17 | Biên dịch & tích hợp |
| 18–19 | Kết quả: dmesg log + /proc & rmmod |
| 20 | Bảng đánh giá tổng hợp |
| 21 | Kết luận |
| 22 | Cảm ơn |

## Chèn ảnh vào slide

Thuyết trình có **4 chỗ placeholder ảnh** (ô "🖼 CHÈN ẢNH") — mở PowerPoint,
xóa ô placeholder và chèn ảnh chụp màn hình thực tế:

| Slide | Gợi ý ảnh |
|---|---|
| 5 | Sơ đồ User space / Kernel space (ring 3 ↔ ring 0) |
| 7 | Sơ đồ luồng gói tin qua network stack |
| 12 | Chụp màn chạy file_manager.sh / tcp_server+client |
| 19 | dmesg -w hiển thị log EMBED và EXTRACT |

## Quy trình làm việc

1. Sửa nội dung trong `BAOCAO.md` (chỉ commit file này).
2. Sửa thông tin trang bìa (thành viên, GVHD) ở đầu `build_docx.py`.
3. Chạy `python build_docx.py` → mở Word → **References → Update Table** để cập nhật mục lục.
4. Chèn ảnh chụp màn hình vào đúng vị trí *[Hình X.X — ...]* trong Chương 4.
