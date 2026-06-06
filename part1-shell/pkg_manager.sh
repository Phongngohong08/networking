#!/bin/bash
# pkg_manager.sh - Cài đặt/gỡ bỏ chương trình tự động (Phần 1)
# Bao boc apt cho cac thao tac thuong dung. Can quyen root.

set -u

usage() {
	cat <<EOF
Cach dung:
  $0 update                 # cap nhat danh sach goi
  $0 upgrade                # nang cap toan he thong
  $0 install <goi1> [goi2]  # cai dat goi
  $0 remove  <goi1> [goi2]  # go bo goi
  $0 search  <tu_khoa>      # tim goi
  $0 batch   <file.txt>     # cai hang loat tu file (moi dong 1 ten goi)
EOF
}

cmd="${1:-}"
shift || true

case "$cmd" in
update)  sudo apt update ;;
upgrade) sudo apt -y upgrade ;;
install) [ $# -eq 0 ] && { usage; exit 1; }; sudo apt install -y "$@" ;;
remove)  [ $# -eq 0 ] && { usage; exit 1; }; sudo apt remove -y "$@" ;;
search)  [ $# -eq 0 ] && { usage; exit 1; }; apt-cache search "$1" ;;
batch)
	[ -z "${1:-}" ] && { usage; exit 1; }
	[ ! -f "$1" ] && { echo "Khong tim thay file: $1"; exit 1; }
	# Bỏ dòng trống và dòng comment (#)
	pkgs=$(grep -vE '^\s*(#|$)' "$1" | tr '\n' ' ')
	echo "Se cai: $pkgs"
	sudo apt install -y $pkgs ;;
*) usage ;;
esac
