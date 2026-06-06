/*
 * file_ops.c - Thao tác file cơ bản bằng syscall (Phần 2)
 * Demo: tạo file, ghi, đọc lại, xem thông tin (stat).
 *
 * Build: make   |   Chạy: ./file_ops <ten_file>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <sys/stat.h>

int main(int argc, char *argv[])
{
	const char *path = (argc > 1) ? argv[1] : "demo.txt";
	const char *msg = "Du lieu test tu file_ops.c\n";
	char buf[256];
	int fd;

	/* Ghi */
	fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (fd < 0) { perror("open(write)"); return 1; }
	if (write(fd, msg, strlen(msg)) < 0) { perror("write"); return 1; }
	close(fd);
	printf("[+] Da ghi '%s'\n", path);

	/* Đọc */
	fd = open(path, O_RDONLY);
	if (fd < 0) { perror("open(read)"); return 1; }
	ssize_t n = read(fd, buf, sizeof(buf) - 1);
	close(fd);
	if (n < 0) { perror("read"); return 1; }
	buf[n] = '\0';
	printf("[+] Noi dung doc duoc: %s", buf);

	/* Thông tin file */
	struct stat st;
	if (stat(path, &st) == 0) {
		printf("[+] Kich thuoc : %ld bytes\n", (long)st.st_size);
		printf("[+] Quyen      : %o\n", st.st_mode & 0777);
		printf("[+] Sua lan cuoi: %s", ctime(&st.st_mtime));
	}

	return 0;
}
