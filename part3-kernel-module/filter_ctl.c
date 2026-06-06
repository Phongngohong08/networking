/*
 * filter_ctl.c - Cong cu user-space dieu khien module net_filter (Bai 2).
 * Gui ioctl toi /dev/netfilter_ctl de dat/xoa IP can chan.
 *
 * Build: gcc -Wall -o filter_ctl filter_ctl.c   (hoac: make filter_ctl)
 * Dung:
 *    sudo ./filter_ctl set 8.8.8.8   # chan moi goi den 8.8.8.8
 *    sudo ./filter_ctl clear         # bo chan
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/ioctl.h>

#define FILTER_IOC_MAGIC 'k'
#define FILTER_SET_ADDR  _IOW(FILTER_IOC_MAGIC, 1, unsigned int)
#define FILTER_CLR_ADDR  _IO(FILTER_IOC_MAGIC, 2)

#define DEV "/dev/netfilter_ctl"

int main(int argc, char *argv[])
{
	if (argc < 2) {
		fprintf(stderr, "Dung: %s set <IP> | clear\n", argv[0]);
		return 1;
	}

	int fd = open(DEV, O_RDWR);
	if (fd < 0) {
		perror("open " DEV " (da insmod net_filter chua? can sudo?)");
		return 1;
	}

	int rc = 0;
	if (strcmp(argv[1], "set") == 0 && argc == 3) {
		struct in_addr a;
		if (inet_pton(AF_INET, argv[2], &a) != 1) {
			fprintf(stderr, "IP khong hop le: %s\n", argv[2]);
			close(fd); return 1;
		}
		unsigned int addr = a.s_addr;   /* network byte order */
		rc = ioctl(fd, FILTER_SET_ADDR, &addr);
		if (rc == 0) printf("Da chan moi goi den %s\n", argv[2]);
	} else if (strcmp(argv[1], "clear") == 0) {
		rc = ioctl(fd, FILTER_CLR_ADDR);
		if (rc == 0) printf("Da bo chan\n");
	} else {
		fprintf(stderr, "Dung: %s set <IP> | clear\n", argv[0]);
		close(fd); return 1;
	}

	if (rc != 0) perror("ioctl");
	close(fd);
	return rc ? 1 : 0;
}
