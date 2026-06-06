/*
 * tcp_server.c - Server TCP đơn giản (Phần 2: socket/network user-space)
 * Lắng nghe trên cổng truyền vào, echo lại dữ liệu client gửi.
 *
 * Build: make   |   Chạy: ./tcp_server 60000
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
	int port = (argc > 1) ? atoi(argv[1]) : 60000;
	int srv, cli;
	struct sockaddr_in addr, peer;
	socklen_t plen = sizeof(peer);
	char buf[BUFSZ];
	int opt = 1;

	srv = socket(AF_INET, SOCK_STREAM, 0);
	if (srv < 0) { perror("socket"); return 1; }

	setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = INADDR_ANY;
	addr.sin_port = htons(port);

	if (bind(srv, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		perror("bind"); return 1;
	}
	if (listen(srv, 5) < 0) { perror("listen"); return 1; }

	printf("[server] Dang lang nghe tai cong %d...\n", port);

	while (1) {
		cli = accept(srv, (struct sockaddr *)&peer, &plen);
		if (cli < 0) { perror("accept"); continue; }

		printf("[server] Client ket noi: %s:%d\n",
		       inet_ntoa(peer.sin_addr), ntohs(peer.sin_port));

		ssize_t n;
		while ((n = recv(cli, buf, BUFSZ - 1, 0)) > 0) {
			buf[n] = '\0';
			printf("[server] Nhan: %s", buf);
			send(cli, buf, n, 0);   /* echo lại */
		}
		close(cli);
		printf("[server] Client ngat ket noi\n");
	}

	close(srv);
	return 0;
}
