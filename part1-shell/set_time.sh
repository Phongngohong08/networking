#!/bin/bash
# set_time.sh - Thiết lập/xem thời gian hệ thống (Phần 1)
# Dùng timedatectl (systemd). Cần quyền root để thay đổi.

set -u

case "${1:-show}" in
show)
	timedatectl ;;
sync)
	# Bật đồng bộ thời gian qua NTP
	sudo timedatectl set-ntp true && echo "Da bat dong bo NTP." ;;
set)
	# Tat NTP roi dat thoi gian thu cong: $0 set "2026-06-06 10:30:00"
	[ -z "${2:-}" ] && { echo "Cach dung: $0 set \"YYYY-MM-DD HH:MM:SS\""; exit 1; }
	sudo timedatectl set-ntp false
	sudo timedatectl set-time "$2" && echo "Da dat thoi gian: $2" ;;
zone)
	# Dat mui gio: $0 zone Asia/Ho_Chi_Minh
	[ -z "${2:-}" ] && { timedatectl list-timezones | grep -i asia; exit 0; }
	sudo timedatectl set-timezone "$2" && echo "Da dat mui gio: $2" ;;
*)
	echo "Cach dung: $0 {show|sync|set \"...\"|zone <TZ>}" ;;
esac
