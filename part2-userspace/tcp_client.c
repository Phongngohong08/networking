/*
 * tcp_client.c - Client TCP (Phần 2: socket/network user-space)
 * Kết nối tới server, gửi dòng nhập từ bàn phím, in phản hồi echo.
 *
 * Build: make   |   Chạy: ./tcp_client 127.0.0.1 60000
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define BUFSZ 1024

int main(int argc, char *argv[])
{
	const char *ip = (argc > 1) ? argv[1] : "127.0.0.1";
	int port = (argc > 2) ? atoi(argv[2]) : 60000;
	int sk;
	struct sockaddr_in addr;
	char buf[BUFSZ];

	sk = socket(AF_INET, SOCK_STREAM, 0);
	if (sk < 0) { perror("socket"); return 1; }

	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = htons(port);
	if (inet_pton(AF_INET, ip, &addr.sin_addr) <= 0) {
		fprintf(stderr, "Dia chi IP khong hop le: %s\n", ip);
		return 1;
	}

	if (connect(sk, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		perror("connect"); return 1;
	}
	printf("[client] Da ket noi %s:%d. Go tin nhan (Ctrl+D de thoat):\n", ip, port);

	while (fgets(buf, BUFSZ, stdin)) {
		send(sk, buf, strlen(buf), 0);
		ssize_t n = recv(sk, buf, BUFSZ - 1, 0);
		if (n <= 0) break;
		buf[n] = '\0';
		printf("[client] Echo: %s", buf);
	}

	close(sk);
	return 0;
}
