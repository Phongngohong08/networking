# Makefile - Phần 2 user-space
CC      = gcc
CFLAGS  = -Wall -Wextra -O2

BINS = tcp_server tcp_client proc_info file_ops

all: $(BINS)

tcp_server: tcp_server.c
	$(CC) $(CFLAGS) -o $@ $<

tcp_client: tcp_client.c
	$(CC) $(CFLAGS) -o $@ $<

proc_info: proc_info.c
	$(CC) $(CFLAGS) -o $@ $<

file_ops: file_ops.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(BINS) demo.txt
