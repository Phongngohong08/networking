# Makefile — steg_net: module giấu tin trong gói TCP
#
# Build:   make
# Nạp:     make load
# Gỡ:      make unload
# Demo:    make demo
# Dọn:     make clean

obj-m += steg_net.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

# Thay đổi peer_ip và secret tuỳ môi trường
PEER   ?= 127.0.0.1
SECRET ?= Hello kernel

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

load: all
	sudo insmod steg_net.ko peer_ip=$(PEER) 'secret="$(SECRET)"'
	@echo "==> Nạp xong. Xem log: sudo dmesg | grep steg"
	@echo "==> Trạng thái: cat /proc/steg_net"

unload:
	sudo rmmod steg_net || true
	@echo "==> Đã gỡ module"

# Demo tự động trên loopback
demo: load
	@echo ""
	@echo "=== Mở listener port 7777 (background) ==="
	nc -l 7777 &
	sleep 0.5
	@echo "=== Gửi dữ liệu TCP (trigger embed) ==="
	echo "steg demo payload" | nc -q1 127.0.0.1 7777 || true
	sleep 0.3
	@echo ""
	@echo "=== /proc/steg_net ==="
	cat /proc/steg_net
	@echo ""
	@echo "=== dmesg (steg) ==="
	sudo dmesg | grep steg | tail -30
	@$(MAKE) unload

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
