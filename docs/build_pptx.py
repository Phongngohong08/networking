#!/usr/bin/env python3
"""
build_pptx.py - Sinh bài thuyết trình (.pptx) cho Đề tài 42.

Nội dung: Giới thiệu → Kiến thức nền (nhân Linux, Netfilter)
          → Steganography mạng → Triển khai steg_net → Kết quả.
Dùng: python build_pptx.py
Yêu cầu: pip install python-pptx
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "ThuyetTrinh_DeTai42_Networking.pptx")

NAVY   = RGBColor(0x1F, 0x47, 0x7C)
BLUE   = RGBColor(0x2E, 0x74, 0xB5)
LIGHT  = RGBColor(0xEA, 0xF1, 0xF8)
CODEBG = RGBColor(0x1E, 0x29, 0x3B)
CODEFG = RGBColor(0x9C, 0xDC, 0xFE)
GRAY   = RGBColor(0x55, 0x55, 0x55)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
PHBG   = RGBColor(0xF3, 0xF6, 0xFA)
PHBD   = RGBColor(0xB5, 0xC7, 0xDD)
GREEN  = RGBColor(0x1E, 0x8A, 0x3C)
MONO   = "Consolas"
SANS   = "Calibri"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK  = prs.slide_layouts[6]


def _set(p, text, size, color, bold=False, font=SANS, align=None):
    p.text = text
    r = p.runs[0]
    r.font.size = Pt(size); r.font.bold = bold
    r.font.color.rgb = color; r.font.name = font
    if align is not None:
        p.alignment = align


def add_box(slide, l, t, w, h, fill=None, line=None, line_w=1.0, round=False):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if round else MSO_SHAPE.RECTANGLE,
        l, t, w, h)
    shp.fill.solid() if fill else shp.fill.background()
    if fill:
        shp.fill.fore_color.rgb = fill
    if line:
        shp.line.color.rgb = line; shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def title_bar(slide, title, kicker=None):
    add_box(slide, 0, 0, SW, Inches(1.15), fill=NAVY)
    add_box(slide, 0, Inches(1.15), SW, Pt(4), fill=BLUE)
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.18),
                                  SW - Inches(1), Inches(0.9))
    tf = tb.text_frame; tf.word_wrap = True
    if kicker:
        _set(tf.paragraphs[0], kicker, 12, RGBColor(0xBF, 0xD6, 0xF0), bold=True)
        p = tf.add_paragraph(); _set(p, title, 26, WHITE, bold=True)
    else:
        _set(tf.paragraphs[0], title, 28, WHITE, bold=True)
        tf.paragraphs[0].space_before = Pt(8)


def footer(slide, idx):
    tb = slide.shapes.add_textbox(Inches(0.4), SH - Inches(0.42),
                                  SW - Inches(0.8), Inches(0.3))
    _set(tb.text_frame.paragraphs[0],
         "Đề tài 42 — Lập trình nhân Linux: Giấu tin trong gói TCP", 9, GRAY)
    n = slide.shapes.add_textbox(SW - Inches(1.2), SH - Inches(0.42),
                                 Inches(0.9), Inches(0.3))
    _set(n.text_frame.paragraphs[0], str(idx), 10, GRAY, align=PP_ALIGN.RIGHT)


_slide_no = 0


def new_slide(title=None, kicker=None, count=True):
    global _slide_no
    s = prs.slides.add_slide(BLANK)
    add_box(s, 0, 0, SW, SH, fill=WHITE)
    if title:
        title_bar(s, title, kicker)
    if count:
        _slide_no += 1
        footer(s, _slide_no)
    return s


def bullets(slide, items, left=Inches(0.7), top=Inches(1.5),
            width=None, size=18, gap=10):
    width = width or (SW - Inches(1.4))
    tb = slide.shapes.add_textbox(left, top, width, SH - top - Inches(0.7))
    tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(items):
        lvl, txt = (1, it[1]) if isinstance(it, tuple) else (0, it)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        _set(p, ("•  " if lvl == 0 else "–  ") + txt,
             size - lvl * 2,
             NAVY if lvl == 0 else GRAY, bold=(lvl == 0))
        p.level = lvl; p.space_after = Pt(gap)
    return tb


def code_box(slide, code, left=Inches(0.6), top=Inches(1.45),
             width=None, height=None, size=12, caption=None):
    width  = width  or (SW - Inches(1.2))
    height = height or Inches(4.3)
    box = add_box(slide, left, top, width, height, fill=CODEBG, round=True)
    tf  = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.2); tf.margin_right = Inches(0.15)
    tf.margin_top  = Inches(0.12); tf.margin_bottom = Inches(0.1)
    for i, line in enumerate(code.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        _set(p, line if line else " ", size, CODEFG, font=MONO,
             align=PP_ALIGN.LEFT)
        p.line_spacing = 1.0; p.space_after = Pt(0)
    if caption:
        cb = slide.shapes.add_textbox(left, top + height + Inches(0.05),
                                      width, Inches(0.35))
        _set(cb.text_frame.paragraphs[0], caption, 11, GRAY, font=MONO)
    return box


def img_ph(slide, suggestion, left=None, top=Inches(1.5),
           width=Inches(5.4), height=Inches(4.6)):
    left = left if left is not None else (SW - width - Inches(0.6))
    box = add_box(slide, left, top, width, height,
                  fill=PHBG, line=PHBD, line_w=1.5, round=True)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.3); tf.margin_right = Inches(0.3)
    _set(tf.paragraphs[0], "🖼  CHÈN ẢNH", 16, BLUE,
         bold=True, align=PP_ALIGN.CENTER)
    p = tf.add_paragraph()
    _set(p, suggestion, 12, GRAY, align=PP_ALIGN.CENTER)
    p.space_before = Pt(8)
    return box


def purpose(slide, text, top=Inches(1.32), width=None):
    width = width or (SW - Inches(1.2))
    box = add_box(slide, Inches(0.6), top, width, Inches(0.7),
                  fill=LIGHT, line=BLUE, line_w=1.0, round=True)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.margin_left = Inches(0.2)
    p = tf.paragraphs[0]
    r  = p.add_run(); r.text = "🎯 Mục đích:  "
    r.font.bold = True; r.font.size = Pt(15); r.font.color.rgb = NAVY
    r2 = p.add_run(); r2.text = text
    r2.font.size = Pt(15); r2.font.color.rgb = GRAY
    return box


# =====================================================================
# SLIDE 1 — TITLE
# =====================================================================
s = new_slide(count=False)
add_box(s, 0, 0, SW, SH, fill=NAVY)
add_box(s, 0, Inches(3.5), SW, Pt(3), fill=BLUE)

tb = s.shapes.add_textbox(Inches(1), Inches(0.9), SW - Inches(2), Inches(0.8))
_set(tb.text_frame.paragraphs[0],
     "HỌC VIỆN KỸ THUẬT MẬT MÃ — KHOA CÔNG NGHỆ THÔNG TIN",
     15, RGBColor(0xBF, 0xD6, 0xF0), bold=True, align=PP_ALIGN.CENTER)

tb = s.shapes.add_textbox(Inches(1), Inches(1.8), SW - Inches(2), Inches(1.0))
_set(tb.text_frame.paragraphs[0], "LẬP TRÌNH NHÂN LINUX",
     30, WHITE, bold=True, align=PP_ALIGN.CENTER)

tb = s.shapes.add_textbox(Inches(1), Inches(3.7), SW - Inches(2), Inches(1.8))
tf = tb.text_frame; tf.word_wrap = True
_set(tf.paragraphs[0], "Đề tài 42",
     22, RGBColor(0x8E, 0xC6, 0xFF), bold=True, align=PP_ALIGN.CENTER)
p = tf.add_paragraph()
_set(p, "Giấu tin trong gói TCP/UDP — Network Steganography",
     18, WHITE, align=PP_ALIGN.CENTER)

tb = s.shapes.add_textbox(Inches(1), Inches(5.7), SW - Inches(2), Inches(1.2))
tf = tb.text_frame
_set(tf.paragraphs[0],
     "Nhóm: Ngô Hồng Phong  ·  Ngô Minh Cường  ·  Đỗ Minh Thuần",
     14, WHITE, align=PP_ALIGN.CENTER)
p = tf.add_paragraph()
_set(p, "Hà Nội, 2026", 13, RGBColor(0xBF, 0xD6, 0xF0), align=PP_ALIGN.CENTER)

# =====================================================================
# SLIDE 2 — AGENDA
# =====================================================================
s = new_slide("Nội dung trình bày")
agenda = [
    ("1", "Tổng quan đề tài",        "Mục tiêu & phạm vi"),
    ("2", "Kiến thức nền",            "Nhân Linux · LKM · Netfilter"),
    ("3", "Steganography mạng",       "Giấu tin trong trường IP ID"),
    ("4", "Triển khai steg_net",      "Thiết kế · Embed · Extract · /proc"),
    ("5", "Kết quả thực nghiệm",      "Build · Demo · Phân tích log"),
    ("6", "Kết luận",                 "Tổng kết & hướng phát triển"),
]
y = Inches(1.55)
for i, (num, title, sub) in enumerate(agenda):
    add_box(s, Inches(0.9), y, Inches(11.5), Inches(0.72),
            fill=(LIGHT if i % 2 == 0 else WHITE), line=PHBD, line_w=0.75, round=True)
    badge = s.shapes.add_shape(MSO_SHAPE.OVAL,
                               Inches(1.08), y + Inches(0.09),
                               Inches(0.54), Inches(0.54))
    badge.fill.solid(); badge.fill.fore_color.rgb = NAVY
    badge.line.fill.background(); badge.shadow.inherit = False
    _set(badge.text_frame.paragraphs[0], num, 20, WHITE,
         bold=True, align=PP_ALIGN.CENTER)
    tb = s.shapes.add_textbox(Inches(1.95), y + Inches(0.02),
                              Inches(10.2), Inches(0.68))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p  = tf.paragraphs[0]
    r  = p.add_run(); r.text = title + "    "
    r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = NAVY
    r2 = p.add_run(); r2.text = sub
    r2.font.size = Pt(13); r2.font.color.rgb = GRAY; r2.font.italic = True
    y += Inches(0.84)

# =====================================================================
# SLIDE 3 — TỔNG QUAN
# =====================================================================
s = new_slide("Tổng quan đề tài", kicker="GIỚI THIỆU")
bullets(s, [
    "Đề tài 42 gồm 3 phần:",
    ("", "Shell: quản lý file, lập lịch, thời gian, cài/gỡ phần mềm"),
    ("", "C user-space: tiến trình, file, socket TCP/UDP"),
    ("", "Module nhân (TRỌNG TÂM): giấu tin trong gói TCP"),
    "Mục tiêu phần module nhân:",
    ("", "Hiểu network stack & cơ chế Netfilter hook"),
    ("", "Đọc/sửa header gói tin qua struct sk_buff"),
    ("", "Triển khai kỹ thuật steganography mạng trong kernel space"),
    ("", "Theo dõi trạng thái module qua /proc"),
], size=17, gap=9)

# =====================================================================
# SLIDE 4 — NHÂN LINUX LÀ GÌ?  (KIẾN THỨC NỀN)
# =====================================================================
s = new_slide("Nhân Linux (Linux Kernel) là gì?", kicker="KIẾN THỨC NỀN")
bullets(s, [
    "Lõi của hệ điều hành — trung gian phần cứng ↔ ứng dụng.",
    "Quản lý: tiến trình, bộ nhớ, file, thiết bị, mạng.",
    "Kiến trúc nguyên khối (monolithic): toàn bộ dịch vụ chạy chung kernel space.",
    "Viết bằng C, mã nguồn mở.",
    "Ứng dụng truy cập phần cứng gián tiếp qua syscall.",
], left=Inches(0.6), width=Inches(6.3), size=17, gap=12)
code_box(s,
    "/* Kiểu hàm xử lý gói trong nhân */\n"
    "\n"
    "typedef unsigned int nf_hookfn(\n"
    "    void *priv,\n"
    "    struct sk_buff *skb,\n"
    "    const struct nf_hook_state *state\n"
    ");\n"
    "\n"
    "/* Trả về NF_ACCEPT hoặc NF_DROP */",
    left=Inches(7.1), width=Inches(5.6), top=Inches(1.7),
    height=Inches(3.3), size=13,
    caption="Nguồn: Linux Kernel Labs — Networking")

# =====================================================================
# SLIDE 5 — KERNEL SPACE vs USER SPACE
# =====================================================================
s = new_slide("Kernel space vs User space", kicker="KIẾN THỨC NỀN")
bullets(s, [
    "Bộ nhớ chia làm 2 vùng tách biệt:",
    ("", "User space (ring 3): ứng dụng thông thường, quyền hạn chế, cô lập."),
    ("", "Kernel space (ring 0): nhân Linux, toàn quyền phần cứng."),
    "Cầu nối: system call (open, read, socket, write...).",
    "Code kernel space:",
    ("", "Truy cập bộ nhớ/phần cứng trực tiếp — không có bảo vệ như user space."),
    ("", "Lỗi → kernel panic  ⇒  luôn test trong máy ảo, snapshot trước."),
], left=Inches(0.6), width=Inches(6.6), size=16, gap=10)
img_ph(s, "Sơ đồ hai vùng User space / Kernel space và syscall làm cầu nối "
          "(ring 3 ↔ ring 0).",
       left=Inches(7.4), width=Inches(5.3), top=Inches(1.5), height=Inches(4.6))

# =====================================================================
# SLIDE 6 — KERNEL MODULE (LKM)
# =====================================================================
s = new_slide("Kernel Module (LKM)", kicker="KIẾN THỨC NỀN")
bullets(s, [
    "Loadable Kernel Module: nạp/gỡ vào nhân lúc chạy, không cần reboot.",
    "Dùng cho: driver, hệ thống file, module mạng (đề tài này).",
    "Lệnh quản lý: insmod / rmmod / lsmod / modinfo / dmesg.",
    "Mỗi module khai báo init và exit.",
], left=Inches(0.6), width=Inches(6.3), size=17, gap=12)
code_box(s,
    "#include <linux/module.h>\n"
    "#include <linux/kernel.h>\n"
    "\n"
    "static int __init my_init(void) {\n"
    "    pr_info(\"module: loaded\\n\");\n"
    "    return 0;\n"
    "}\n"
    "static void __exit my_exit(void) {\n"
    "    pr_info(\"module: unloaded\\n\");\n"
    "}\n"
    "\n"
    "module_init(my_init);\n"
    "module_exit(my_exit);\n"
    "MODULE_LICENSE(\"GPL\");",
    left=Inches(7.1), width=Inches(5.6), top=Inches(1.5),
    height=Inches(4.7), size=13,
    caption="Khung cơ bản của một kernel module")

# =====================================================================
# SLIDE 7 — HỆ THỐNG MẠNG TRONG LINUX
# =====================================================================
s = new_slide("Hệ thống mạng trong Linux", kicker="KIẾN THỨC NỀN")
bullets(s, [
    "Toàn bộ truyền thông mạng do nhân điều phối.",
    "Gói tin nhận đi qua: NIC → driver → tầng IP → TCP/UDP → socket.",
    "Mỗi tầng bọc/gỡ header (Ethernet, IP, TCP/UDP).",
    "Kể cả lưu lượng localhost (127.0.0.1) cũng đi qua nhân.",
    "→ Module nhân có thể quan sát/sửa MỌI gói tin.",
], left=Inches(0.6), width=Inches(6.6), size=17, gap=11)
img_ph(s, "Sơ đồ luồng gói tin: NIC → driver → IP → TCP/UDP → socket → app "
          "(từ trang Linux Kernel Labs).",
       left=Inches(7.4), width=Inches(5.3), top=Inches(1.5), height=Inches(4.6))

# =====================================================================
# SLIDE 8 — NETFILTER & IPTABLES
# =====================================================================
s = new_slide("Netfilter & iptables — bức tranh lớn", kicker="KIẾN THỨC NỀN")
bullets(s, [
    "Netfilter: khung lọc gói tích hợp sẵn trong nhân Linux.",
    "iptables/nftables là công cụ user-space cấu hình Netfilter.",
    "5 điểm hook IPv4: PRE_ROUTING, LOCAL_IN, FORWARD, LOCAL_OUT, POST_ROUTING.",
    "Module steg_net đăng ký hook ở 2 điểm:",
    ("", "LOCAL_OUT  → bắt gói đi ra để nhúng tin"),
    ("", "PRE_ROUTING → bắt gói đến để trích tin"),
], left=Inches(0.6), width=Inches(6.3), size=15, gap=11)
code_box(s,
    "static struct nf_hook_ops my_ops = {\n"
    "    .hook     = my_hook_fn,\n"
    "    .pf       = PF_INET,\n"
    "    .hooknum  = NF_INET_LOCAL_OUT,\n"
    "    .priority = NF_IP_PRI_FIRST,\n"
    "};\n"
    "\n"
    "/* Đăng ký vào init() */\n"
    "nf_register_net_hook(&init_net, &my_ops);\n"
    "\n"
    "/* Gỡ trong exit() */\n"
    "nf_unregister_net_hook(&init_net, &my_ops);",
    left=Inches(7.1), width=Inches(5.6), top=Inches(1.5),
    height=Inches(4.5), size=12.5,
    caption="Nguồn: Linux Kernel Labs — Networking")

# =====================================================================
# SLIDE 9 — SK_BUFF
# =====================================================================
s = new_slide("struct sk_buff — gói tin trong nhân", kicker="CƠ SỞ LÝ THUYẾT")
bullets(s, [
    "sk_buff (socket buffer): cấu trúc trung tâm biểu diễn 1 gói tin.",
    "Chứa dữ liệu + con trỏ tới từng tầng header.",
    "Hàm truy cập header:",
    ("", "ip_hdr(skb)   →  struct iphdr  (saddr, daddr, id, protocol)"),
    ("", "tcp_hdr(skb)  →  struct tcphdr (source, dest, SYN/ACK/FIN)"),
    ("", "udp_hdr(skb)  →  struct udphdr (source, dest)"),
    "Trường id (IP ID, 16-bit) là vật chứa dùng để giấu tin.",
], size=17, gap=10)

# =====================================================================
# SLIDE 10 — STEGANOGRAPHY LÀ GÌ?
# =====================================================================
s = new_slide("Steganography — Giấu tin là gì?", kicker="STEGANOGRAPHY MẠNG")
bullets(s, [
    "Kỹ thuật ẩn thông điệp trong một vật chứa (carrier).",
    "Khác mã hóa: bề ngoài dữ liệu không thay đổi — người ngoài không biết có tin ẩn.",
    "Steganography mạng: dùng trường dư thừa trong header gói tin.",
    "Vật chứa phổ biến trong gói tin:",
    ("", "Trường IP Identification (16-bit) — ít dùng khi không phân mảnh"),
    ("", "TCP Reserved bits — các bit dự phòng"),
    ("", "IP TTL — giá trị giảm dần theo hops"),
    ("", "Timing covert channel — khoảng cách thời gian giữa gói"),
    "Đề tài dùng: IP ID  (đơn giản, hiệu quả, không ảnh hưởng định tuyến)",
], size=16, gap=9)

# =====================================================================
# SLIDE 11 — KỸ THUẬT IP ID
# =====================================================================
s = new_slide("Kỹ thuật: nhúng tin vào trường IP ID", kicker="STEGANOGRAPHY MẠNG")
bullets(s, [
    "IP ID (16-bit): RFC 791 dùng để tái hợp phân mảnh.",
    "Với gói không phân mảnh → nhân gán giá trị ngẫu nhiên → có thể thay thế.",
    "Encoding của steg_net:",
    ("", "Byte cao (bit 15-8) = 0xAB  ← magic marker để nhận ra 'gói steg'"),
    ("", "Byte thấp (bit 7-0) = ký tự thứ pos của secret"),
], left=Inches(0.6), width=Inches(6.5), size=16, gap=11)
code_box(s,
    "/* Ví dụ: secret = \"HELLO\" */\n"
    "\n"
    "Gói 1:  IP_ID = 0xAB48  ('H' = 0x48)\n"
    "Gói 2:  IP_ID = 0xAB45  ('E' = 0x45)\n"
    "Gói 3:  IP_ID = 0xAB4C  ('L' = 0x4C)\n"
    "Gói 4:  IP_ID = 0xAB4C  ('L' = 0x4C)\n"
    "Gói 5:  IP_ID = 0xAB4F  ('O' = 0x4F)\n"
    "\n"
    "/* Sau khi sửa IP ID: */\n"
    "iph->check = 0;\n"
    "iph->check = ip_fast_csum((u8*)iph, iph->ihl);",
    left=Inches(7.1), top=Inches(1.5), width=Inches(5.6),
    height=Inches(4.5), size=13,
    caption="Phải tính lại IP checksum sau khi sửa header")

# =====================================================================
# SLIDE 12 — PHẦN 1+2 TÓM TẮT
# =====================================================================
s = new_slide("Phần 1 & 2 — Shell và C user-space", kicker="TỔNG QUAN TRIỂN KHAI")
# Chia đôi slide: left = shell, right = C
left_items = [
    "Lập trình Shell (Phần 1):",
    ("", "file_manager.sh — quản lý file/thư mục, sao lưu"),
    ("", "scheduler.sh   — cron & at lập lịch"),
    ("", "set_time.sh    — timedatectl, NTP"),
    ("", "pkg_manager.sh — apt cài/gỡ hàng loạt"),
]
right_items = [
    "Lập trình C user-space (Phần 2):",
    ("", "proc_info.c  — đọc /proc/<pid>/status"),
    ("", "file_ops.c   — open/read/write/stat"),
    ("", "tcp_server.c — socket TCP, echo"),
    ("", "tcp_client.c — kết nối TCP, gửi data"),
]
bullets(s, left_items,  left=Inches(0.6), width=Inches(5.9), size=15, gap=10)
bullets(s, right_items, left=Inches(6.8), width=Inches(6.1), size=15, gap=10)
add_box(s, Inches(6.6), Inches(1.5), Pt(1.5), Inches(4.8), fill=PHBD)

# =====================================================================
# SLIDE 13 — STEG_NET: THIẾT KẾ TỔNG QUAN
# =====================================================================
s = new_slide("steg_net — Thiết kế tổng quan", kicker="TRIỂN KHAI MODULE NHÂN")
purpose(s, "Module nhân duy nhất: nhúng/trích thông điệp ẩn trong gói TCP, "
           "không cần công cụ user-space bổ sung.")
bullets(s, [
    "Hai Netfilter hook:",
    ("", "embed_hook  @ LOCAL_OUT   → gói TCP ra → ghi secret[pos] vào IP ID"),
    ("", "extract_hook @ PRE_ROUTING → gói TCP đến → đọc IP ID, ghép thông điệp"),
    "Theo dõi qua /proc/steg_net (trạng thái embed_pos, extracted).",
    "Tham số nạp module: peer_ip (bắt buộc), secret (chuỗi cần giấu).",
    "Dùng spinlock bảo vệ buffer extracted (hook chạy trong softirq).",
], top=Inches(2.2), size=16, gap=10)

# =====================================================================
# SLIDE 14 — EMBED CODE
# =====================================================================
s = new_slide("steg_net — Hàm EMBED", kicker="TRIỂN KHAI MODULE NHÂN")
purpose(s, "Mỗi gói TCP tới peer_ip → thay IP ID bằng magic+ký_tự → tính lại checksum.")
code_box(s,
    "static unsigned int embed_hook(void *priv,\n"
    "        struct sk_buff *skb,\n"
    "        const struct nf_hook_state *state)\n"
    "{\n"
    "    struct iphdr *iph = ip_hdr(skb);\n"
    "    if (!iph || iph->protocol != IPPROTO_TCP) return NF_ACCEPT;\n"
    "    if (iph->daddr != peer_addr) return NF_ACCEPT;\n"
    "\n"
    "    int pos = atomic_inc_return(&embed_pos) - 1;\n"
    "    pos  = pos % secret_len;\n"
    "    u16 new_id = ((u16)0xAB << 8) | (u8)secret[pos];\n"
    "\n"
    "    iph->id    = htons(new_id);   /* nhúng ký tự */\n"
    "    iph->check = 0;\n"
    "    iph->check = ip_fast_csum((u8*)iph, iph->ihl);\n"
    "\n"
    "    pr_info(\"steg [EMBED] pos=%d char='%c' ID=0x%04X\\n\",\n"
    "            pos, secret[pos], new_id);\n"
    "    return NF_ACCEPT;\n"
    "}",
    top=Inches(2.2), height=Inches(4.5), size=12)

# =====================================================================
# SLIDE 15 — EXTRACT CODE
# =====================================================================
s = new_slide("steg_net — Hàm EXTRACT", kicker="TRIỂN KHAI MODULE NHÂN")
purpose(s, "Gói TCP đến từ peer_ip có IP ID high byte = 0xAB → trích ký tự ẩn.")
code_box(s,
    "static unsigned int extract_hook(void *priv,\n"
    "        struct sk_buff *skb,\n"
    "        const struct nf_hook_state *state)\n"
    "{\n"
    "    struct iphdr *iph = ip_hdr(skb);\n"
    "    if (!iph || iph->protocol != IPPROTO_TCP) return NF_ACCEPT;\n"
    "    if (iph->saddr != peer_addr) return NF_ACCEPT;\n"
    "\n"
    "    u16 ip_id = ntohs(iph->id);\n"
    "    u8  magic = (ip_id >> 8) & 0xFF;\n"
    "    u8  ch    =  ip_id       & 0xFF;\n"
    "\n"
    "    if (magic != 0xAB) return NF_ACCEPT; /* không phải gói steg */\n"
    "\n"
    "    spin_lock(&extract_lock);\n"
    "    extracted[extract_pos++] = ch;\n"
    "    extracted[extract_pos]   = '\\0';\n"
    "    spin_unlock(&extract_lock);\n"
    "\n"
    "    pr_info(\"steg [EXTRACT] ID=0x%04X char='%c'\\n\", ip_id, ch);\n"
    "    return NF_ACCEPT;\n"
    "}",
    top=Inches(2.2), height=Inches(4.5), size=11.5)

# =====================================================================
# SLIDE 16 — INIT, EXIT & /PROC
# =====================================================================
s = new_slide("steg_net — Init, Exit & /proc", kicker="TRIỂN KHAI MODULE NHÂN")
code_box(s,
    "static int __init steg_init(void)\n"
    "{\n"
    "    /* kiểm tra peer_ip, parse địa chỉ */\n"
    "    in4_pton(peer_ip, -1, (u8*)&peer_addr, -1, NULL);\n"
    "    secret_len = strlen(secret);\n"
    "\n"
    "    nf_register_net_hook(&init_net, &embed_ops);\n"
    "    nf_register_net_hook(&init_net, &extract_ops);\n"
    "    proc_create(\"steg_net\", 0444, NULL, &steg_proc_ops);\n"
    "\n"
    "    pr_info(\"steg_net: loaded peer=%pI4\\n\", &peer_addr);\n"
    "    return 0;\n"
    "}\n"
    "static void __exit steg_exit(void)\n"
    "{\n"
    "    remove_proc_entry(\"steg_net\", NULL);\n"
    "    nf_unregister_net_hook(&init_net, &extract_ops);\n"
    "    nf_unregister_net_hook(&init_net, &embed_ops);\n"
    "    pr_info(\"steg_net: extracted=\\\"%s\\\"\\n\", extracted);\n"
    "}",
    top=Inches(1.45), height=Inches(4.8), width=Inches(7.3), size=11.5)
code_box(s,
    "# Xem trạng thái:\n"
    "cat /proc/steg_net\n"
    "\n"
    "=== steg_net status ===\n"
    "secret    : \"HELLO\" (5 bytes)\n"
    "peer_ip   : 127.0.0.1\n"
    "magic     : 0xAB\n"
    "embed_pos : 3\n"
    "extracted : \"HEL\"",
    left=Inches(7.7), top=Inches(1.45), width=Inches(5.2),
    height=Inches(3.2), size=12,
    caption="/proc/steg_net hiển thị tiến độ realtime")

# =====================================================================
# SLIDE 17 — BUILD & TÍCH HỢP
# =====================================================================
s = new_slide("Biên dịch & tích hợp vào nhân", kicker="THỰC NGHIỆM")
bullets(s, [
    "Cài đặt phụ thuộc:",
], left=Inches(0.6), width=Inches(12), size=17, gap=8)
code_box(s,
    "sudo apt install build-essential linux-headers-$(uname -r)",
    top=Inches(2.15), height=Inches(0.65), size=14)
bullets(s, [
    "Biên dịch và nạp module:",
], left=Inches(0.6), top=Inches(3.0), width=Inches(12), size=17, gap=8)
code_box(s,
    "cd part3-kernel-module\n"
    "make                           # → steg_net.ko\n"
    "sudo insmod steg_net.ko peer_ip=127.0.0.1 'secret=\"HELLO\"'\n"
    "lsmod | grep steg_net          # xác nhận đã nạp\n"
    "dmesg | grep steg              # xem log",
    top=Inches(3.55), height=Inches(2.0), size=13.5)
bx = s.shapes.add_textbox(Inches(0.6), Inches(5.8), Inches(12), Inches(0.55))
_set(bx.text_frame.paragraphs[0],
     "⚠  Cảnh báo 'Skipping BTF generation' khi make là vô hại — không ảnh hưởng hoạt động module.",
     13, GRAY)

# =====================================================================
# SLIDE 18 — DEMO LOG
# =====================================================================
s = new_slide("Kết quả — Nhật ký kernel (dmesg)", kicker="THỰC NGHIỆM")
bullets(s, [
    "Thiết lập demo (1 VM, loopback 127.0.0.1):",
], left=Inches(0.6), width=Inches(12), size=16, gap=8)
code_box(s,
    "# Terminal 1: mở listener\n"
    "nc -l 7777\n"
    "\n"
    "# Terminal 2: gửi dữ liệu TCP\n"
    "echo \"test\" | nc 127.0.0.1 7777",
    top=Inches(2.1), height=Inches(1.65), width=Inches(5.8), size=13)
bullets(s, [
    "Nhật ký dmesg:",
], left=Inches(0.6), top=Inches(3.95), width=Inches(12), size=16, gap=8)
code_box(s,
    "steg_net: loaded — secret=\"HELLO\" peer=127.0.0.1\n"
    "steg [EMBED] pos=0  char='H'(0x48)  IP_ID=0xAB48\n"
    "steg [EMBED] pos=1  char='E'(0x45)  IP_ID=0xAB45\n"
    "steg [EMBED] pos=2  char='L'(0x4C)  IP_ID=0xAB4C\n"
    "steg [EXTRACT] IP_ID=0xAB48  char='H'  from 127.0.0.1\n"
    "steg [EXTRACT] IP_ID=0xAB45  char='E'  from 127.0.0.1",
    top=Inches(4.5), height=Inches(2.0), size=12.5)

# =====================================================================
# SLIDE 19 — KẾT QUẢ /PROC + RMMOD
# =====================================================================
s = new_slide("Kết quả — /proc & rmmod", kicker="THỰC NGHIỆM")
bullets(s, [
    "Xem trạng thái realtime:",
], left=Inches(0.6), width=Inches(6.4), size=16, gap=8)
code_box(s,
    "cat /proc/steg_net\n"
    "\n"
    "=== steg_net status ===\n"
    "secret    : \"HELLO\" (5 bytes)\n"
    "peer_ip   : 127.0.0.1 (127.0.0.1)\n"
    "magic     : 0xAB\n"
    "embed_pos : 2 (ký tự tiếp: 'L')\n"
    "extracted : \"HE\" (2 bytes)",
    left=Inches(0.6), top=Inches(2.1), width=Inches(5.8), height=Inches(3.0), size=12.5)
bullets(s, [
    "Gỡ module → in thông điệp trích xuất đầy đủ:",
], left=Inches(6.7), top=Inches(1.5), width=Inches(6.2), size=16, gap=8)
code_box(s,
    "sudo rmmod steg_net\n"
    "\n"
    "# dmesg:\n"
    "steg_net: đã trích xuất: \"HELLO\"\n"
    "steg_net: unloaded",
    left=Inches(6.7), top=Inches(2.1), width=Inches(5.9), height=Inches(2.0), size=13)
img_ph(s, "Ảnh chụp terminal: dmesg -w hiển thị toàn bộ quá trình "
          "EMBED và EXTRACT từng ký tự.",
       left=Inches(6.7), top=Inches(4.3), width=Inches(5.9), height=Inches(2.2))

# =====================================================================
# SLIDE 20 — ĐÁNH GIÁ TỔNG HỢP
# =====================================================================
s = new_slide("Đánh giá tổng hợp", kicker="ĐÁNH GIÁ")
rows = [
    ("Yêu cầu", "Kết quả"),
    ("Xây dựng module nhân, nạp/gỡ ổn định", "Đạt"),
    ("Đăng ký 2 Netfilter hook (LOCAL_OUT, PRE_ROUTING)", "Đạt"),
    ("Nhúng ký tự vào IP ID, tính lại checksum", "Đạt"),
    ("Trích xuất và tái tạo thông điệp từ gói đến", "Đạt"),
    ("Theo dõi trạng thái qua /proc/steg_net", "Đạt"),
    ("Không gây crash nhân, gỡ module sạch", "Đạt"),
]
t = s.shapes.add_table(len(rows), 2,
                       Inches(1.0), Inches(1.6),
                       Inches(11.3), Inches(4.5)).table
t.columns[0].width = Inches(8.8)
t.columns[1].width = Inches(2.5)
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        c = t.cell(i, j); c.text = val
        p = c.text_frame.paragraphs[0]; r = p.runs[0]
        r.font.size = Pt(16 if i > 0 else 17)
        r.font.name = SANS
        if i == 0:
            r.font.bold = True; r.font.color.rgb = WHITE
            c.fill.solid(); c.fill.fore_color.rgb = NAVY
        else:
            r.font.color.rgb = GRAY
            if j == 1:
                r.font.bold = True; r.font.color.rgb = GREEN

# =====================================================================
# SLIDE 21 — KẾT LUẬN
# =====================================================================
s = new_slide("Kết luận & hướng phát triển", kicker="KẾT LUẬN")
bullets(s, [
    "Đề tài hoàn thành 3 phần:",
    ("", "Shell: 4 script tự động hoá quản trị hệ thống"),
    ("", "C user-space: tiến trình, file, socket TCP"),
    ("", "Module nhân steg_net: giấu tin trong IP ID của gói TCP"),
    "Qua đề tài, nhóm nắm được:",
    ("", "Vòng đời module nhân (insmod/rmmod, init/exit)"),
    ("", "Kiến trúc network stack & cấu trúc sk_buff"),
    ("", "Đăng ký/gỡ Netfilter hook an toàn với spinlock"),
    ("", "Kỹ thuật steganography mạng thực tế"),
    "Hướng phát triển:",
    ("", "Giấu tin trong TCP Sequence Number (băng thông ẩn cao hơn)"),
    ("", "Mã hóa secret trước khi nhúng để tăng bảo mật"),
    ("", "Hỗ trợ IPv6"),
], size=15, gap=8)

# =====================================================================
# SLIDE 22 — CẢM ƠN
# =====================================================================
s = new_slide(count=False)
add_box(s, 0, 0, SW, SH, fill=NAVY)
add_box(s, 0, Inches(3.3), SW, Pt(3), fill=BLUE)
tb = s.shapes.add_textbox(Inches(1), Inches(2.5), SW - Inches(2), Inches(1.5))
_set(tb.text_frame.paragraphs[0],
     "CẢM ƠN THẦY/CÔ & CÁC BẠN", 38, WHITE,
     bold=True, align=PP_ALIGN.CENTER)
tb = s.shapes.add_textbox(Inches(1), Inches(4.1), SW - Inches(2), Inches(1))
_set(tb.text_frame.paragraphs[0],
     "ĐÃ LẮNG NGHE  —  Q & A",
     22, RGBColor(0x8E, 0xC6, 0xFF), align=PP_ALIGN.CENTER)

prs.save(OUT)
print(f"Da tao: {OUT}  |  {len(prs.slides._sldIdLst)} slides")
