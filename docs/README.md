# docs — Báo cáo đề tài

| File | Vai trò |
|---|---|
| `BAOCAO.md` | **Nguồn** báo cáo (Markdown) — commit lên git, dễ sửa/diff |
| `build_docx.py` | Script sinh file Word từ `BAOCAO.md` |
| `BaoCao_DeTai42_Networking.docx` | File Word để nộp — **được gitignore**, sinh lại bằng script |
| `build_pptx.py` | Script sinh bài thuyết trình (24 slide) |
| `ThuyetTrinh_DeTai42_Networking.pptx` | Slide để trình bày — **được gitignore**, sinh lại bằng script |

## Sinh lại file Word / Slide

```bash
pip install python-docx python-pptx   # nếu chưa có
cd docs
python build_docx.py    # -> BaoCao_DeTai42_Networking.docx
python build_pptx.py    # -> ThuyetTrinh_DeTai42_Networking.pptx (24 slide)
```

Bài thuyết trình có **8 chỗ chèn ảnh** (ô "🖼 CHÈN ẢNH" kèm gợi ý nội dung) —
mở PowerPoint, xóa ô placeholder và chèn ảnh thật vào đúng vị trí.

File `BaoCao_DeTai42_Networking.docx` sẽ được tạo lại. Sau khi mở trong Word:

- Vào **References → Table of Contents** để chèn mục lục tự động (các tiêu đề đã
  được đánh style Heading 1/2/3 sẵn).
- Chèn ảnh chụp màn hình vào đúng các vị trí *[Hình 4.x — ...]* trong Chương 4.

## Quy trình làm việc

1. Sửa nội dung trong `BAOCAO.md` (chỉ commit file này).
2. Sửa thông tin trang bìa (thành viên, GVHD...) ở đầu `build_docx.py`.
3. Chạy `python build_docx.py` để xuất bản Word mới trước khi nộp.
