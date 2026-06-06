#!/bin/bash
# scheduler.sh - Lập lịch tác vụ bằng cron/at (Phần 1)
# Thêm/xem/xóa cron job cho user hiện tại.

set -u

usage() {
	cat <<EOF
Cach dung:
  $0 list                          # xem cac cron job hien tai
  $0 add "<lich cron>" "<lenh>"    # them job, vd: "*/5 * * * *" "echo hi >> /tmp/log"
  $0 clear                         # xoa toan bo cron job cua user
  $0 once "<thoi diem>" "<lenh>"   # chay 1 lan bang at, vd: "now + 2 minutes"
EOF
}

case "${1:-}" in
list)
	echo "== Cron job hien tai =="
	crontab -l 2>/dev/null || echo "(chua co job nao)" ;;
add)
	[ $# -lt 3 ] && { usage; exit 1; }
	( crontab -l 2>/dev/null; echo "$2 $3" ) | crontab -
	echo "Da them job: $2 $3" ;;
clear)
	crontab -r 2>/dev/null && echo "Da xoa toan bo cron job." ;;
once)
	[ $# -lt 3 ] && { usage; exit 1; }
	echo "$3" | at $2 && echo "Da len lich at: $2" ;;
*)
	usage ;;
esac
