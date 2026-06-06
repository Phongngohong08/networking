// SPDX-License-Identifier: GPL-2.0
/*
 * ksock_tcp.c - Bai 3 + 4: Tao socket TCP trong kernel, lang nghe cong 60000,
 *               chap nhan ket noi va doc du lieu client gui.
 *
 * Module chay mot kernel thread: tao socket -> bind -> listen -> vong lap
 * accept (non-blocking) -> recv -> in du lieu ra dmesg.
 *
 * Test tu user-space:  nc 127.0.0.1 60000   (roi go vai dong)
 *                  hoac telnet 127.0.0.1 60000
 *
 * Tham khao: https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/net.h>
#include <linux/in.h>
#include <linux/socket.h>
#include <net/sock.h>

#define MODNAME "ksock_tcp"
#define PORT    60000
#define BUFSZ   512

static struct socket *listen_sock;
static struct task_struct *srv_thread;

/* Doc du lieu tu mot ket noi da accept */
static void handle_conn(struct socket *conn)
{
	struct kvec vec;
	struct msghdr msg;
	char *buf;
	int len;

	buf = kmalloc(BUFSZ, GFP_KERNEL);
	if (!buf)
		return;

	memset(&msg, 0, sizeof(msg));
	vec.iov_base = buf;
	vec.iov_len  = BUFSZ - 1;

	len = kernel_recvmsg(conn, &msg, &vec, 1, BUFSZ - 1, 0);
	if (len > 0) {
		buf[len] = '\0';
		pr_info("%s: nhan %d byte: %s\n", MODNAME, len, buf);
	} else if (len < 0) {
		pr_info("%s: kernel_recvmsg loi %d\n", MODNAME, len);
	}

	kfree(buf);
}

static int server_fn(void *data)
{
	struct sockaddr_in addr;
	struct socket *conn;
	int ret;

	ret = sock_create_kern(&init_net, AF_INET, SOCK_STREAM, IPPROTO_TCP,
			       &listen_sock);
	if (ret < 0) {
		pr_err("%s: sock_create_kern loi %d\n", MODNAME, ret);
		return ret;
	}

	memset(&addr, 0, sizeof(addr));
	addr.sin_family      = AF_INET;
	addr.sin_addr.s_addr = htonl(INADDR_ANY);
	addr.sin_port        = htons(PORT);

	ret = kernel_bind(listen_sock, (struct sockaddr *)&addr, sizeof(addr));
	if (ret < 0) {
		pr_err("%s: kernel_bind loi %d\n", MODNAME, ret);
		goto out;
	}

	ret = kernel_listen(listen_sock, 5);
	if (ret < 0) {
		pr_err("%s: kernel_listen loi %d\n", MODNAME, ret);
		goto out;
	}

	pr_info("%s: dang lang nghe TCP cong %d\n", MODNAME, PORT);

	/* Vong lap accept khong chan de rmmod sach */
	while (!kthread_should_stop()) {
		ret = kernel_accept(listen_sock, &conn, O_NONBLOCK);
		if (ret == -EAGAIN) {
			msleep(200);
			continue;
		}
		if (ret < 0) {
			pr_info("%s: kernel_accept loi %d\n", MODNAME, ret);
			msleep(200);
			continue;
		}

		pr_info("%s: co client ket noi\n", MODNAME);
		handle_conn(conn);
		sock_release(conn);
	}

out:
	if (listen_sock) {
		sock_release(listen_sock);
		listen_sock = NULL;
	}
	return ret;
}

static int __init ksock_tcp_init(void)
{
	srv_thread = kthread_run(server_fn, NULL, "ksock_tcp_srv");
	if (IS_ERR(srv_thread)) {
		pr_err("%s: khong tao duoc kernel thread\n", MODNAME);
		return PTR_ERR(srv_thread);
	}
	pr_info("%s: loaded\n", MODNAME);
	return 0;
}

static void __exit ksock_tcp_exit(void)
{
	if (srv_thread)
		kthread_stop(srv_thread);   /* server_fn se thoat & release sock */
	pr_info("%s: unloaded\n", MODNAME);
}

module_init(ksock_tcp_init);
module_exit(ksock_tcp_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Nhom de tai 42 - L02 2026");
MODULE_DESCRIPTION("Bai 3+4: TCP listen/accept trong kernel space");
MODULE_VERSION("1.0");
