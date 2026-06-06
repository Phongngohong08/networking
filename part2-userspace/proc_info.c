/*
 * proc_info.c - Quản lý/xem thông tin tiến trình (Phần 2)
 * Liệt kê các tiến trình đang chạy bằng cách đọc /proc.
 *
 * Build: make   |   Chạy: ./proc_info
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <dirent.h>

int main(void)
{
	DIR *d = opendir("/proc");
	struct dirent *e;

	if (!d) { perror("opendir /proc"); return 1; }

	printf("%-8s %-20s %s\n", "PID", "TEN", "TRANG THAI");
	printf("---------------------------------------------\n");

	while ((e = readdir(d))) {
		/* chỉ lấy thư mục có tên là số (PID) */
		if (!isdigit((unsigned char)e->d_name[0]))
			continue;

		char path[300], name[256] = "?", state = '?';
		snprintf(path, sizeof(path), "/proc/%s/stat", e->d_name);

		FILE *f = fopen(path, "r");
		if (!f) continue;
		/* định dạng: pid (comm) state ... */
		fscanf(f, "%*d (%255[^)]) %c", name, &state);
		fclose(f);

		printf("%-8s %-20.20s %c\n", e->d_name, name, state);
	}

	closedir(d);
	return 0;
}
