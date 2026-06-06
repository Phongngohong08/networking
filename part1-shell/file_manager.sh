#!/bin/bash
# file_manager.sh - Quản lý file/thư mục (Phần 1)
# Menu đơn giản: liệt kê, tạo, xóa, tìm, sao lưu.

set -u

menu() {
	echo "===== QUAN LY FILE ====="
	echo "1) Liet ke file trong thu muc"
	echo "2) Tao file/thu muc"
	echo "3) Xoa file/thu muc"
	echo "4) Tim file theo ten"
	echo "5) Sao luu thu muc (tar.gz)"
	echo "0) Thoat"
	echo "========================"
}

while true; do
	menu
	read -rp "Chon: " choice
	case "$choice" in
	1) read -rp "Thu muc [.]: " d; ls -lah "${d:-.}" ;;
	2) read -rp "Ten (them / o cuoi de tao thu muc): " p
	   if [[ "$p" == */ ]]; then mkdir -p "$p" && echo "Da tao thu muc $p"
	   else touch "$p" && echo "Da tao file $p"; fi ;;
	3) read -rp "Duong dan can xoa: " p; rm -ri "$p" ;;
	4) read -rp "Thu muc tim [.]: " d; read -rp "Ten can tim: " n
	   find "${d:-.}" -iname "*${n}*" ;;
	5) read -rp "Thu muc can sao luu: " d
	   bak="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
	   tar -czf "$bak" "$d" && echo "Da tao $bak" ;;
	0) echo "Tam biet."; break ;;
	*) echo "Lua chon khong hop le." ;;
	esac
	echo
done
