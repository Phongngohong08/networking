# Makefile cho cac kernel module (Bai 1-5) + cong cu user-space
# Build: make    |    Clean: make clean

# Moi dong .o se bien dich thanh mot .ko rieng
obj-m += net_monitor.o     # Bai 1: giam sat packet
obj-m += net_filter.o      # Bai 2: loc packet theo IP dich (ioctl)
obj-m += ksock_tcp.o       # Bai 3+4: TCP listen/accept trong kernel
obj-m += ksock_udp.o       # Bai 5: gui UDP tu kernel

KDIR := /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all: modules filter_ctl

modules:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Cong cu user-space dieu khien net_filter (Bai 2)
filter_ctl: filter_ctl.c
	gcc -Wall -O2 -o filter_ctl filter_ctl.c

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f filter_ctl
