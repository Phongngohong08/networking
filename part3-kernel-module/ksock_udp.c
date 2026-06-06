// SPDX-License-Identifier: GPL-2.0
/*
 * ksock_udp.c - Bai 5: Gui mot tin nhan UDP tu kernel space.
 *
 * Khi nap module, no tao mot socket UDP trong kernel va gui chuoi toi
 * dia chi/cong cau hinh qua module param (mac dinh 127.0.0.1:5005).
 *
 * Test: mo truoc mot listener o user-space roi moi insmod:
 *    nc -u -l 5005
 * roi:
 *    sudo insmod ksock_udp.ko dip="127.0.0.1" dport=5005 msg="Xin chao tu kernel"
 *
 * Tham khao: https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/net.h>
#include <linux/in.h>
#include <linux/inet.h>
#include <net/sock.h>

#define MODNAME "ksock_udp"

static char *dip = "127.0.0.1";
static int   dport = 5005;
static char *msg = "Xin chao tu kernel space (UDP)\n";

module_param(dip, charp, 0444);
MODULE_PARM_DESC(dip, "Dia chi IP dich");
module_param(dport, int, 0444);
MODULE_PARM_DESC(dport, "Cong dich");
module_param(msg, charp, 0444);
MODULE_PARM_DESC(msg, "Noi dung tin nhan");

static int send_udp(void)
{
	struct socket *sock;
	struct sockaddr_in addr;
	struct msghdr mhdr;
	struct kvec vec;
	int ret;

	ret = sock_create_kern(&init_net, AF_INET, SOCK_DGRAM, IPPROTO_UDP,
			       &sock);
	if (ret < 0) {
		pr_err("%s: sock_create_kern loi %d\n", MODNAME, ret);
		return ret;
	}

	memset(&addr, 0, sizeof(addr));
	addr.sin_family      = AF_INET;
	addr.sin_port        = htons(dport);
	addr.sin_addr.s_addr = in_aton(dip);   /* chuoi IP -> __be32 */

	memset(&mhdr, 0, sizeof(mhdr));
	mhdr.msg_name    = &addr;
	mhdr.msg_namelen = sizeof(addr);

	vec.iov_base = msg;
	vec.iov_len  = strlen(msg);

	ret = kernel_sendmsg(sock, &mhdr, &vec, 1, vec.iov_len);
	if (ret < 0)
		pr_err("%s: kernel_sendmsg loi %d\n", MODNAME, ret);
	else
		pr_info("%s: da gui %d byte toi %s:%d\n",
			MODNAME, ret, dip, dport);

	sock_release(sock);
	return ret;
}

static int __init ksock_udp_init(void)
{
	pr_info("%s: loaded - gui UDP toi %s:%d\n", MODNAME, dip, dport);
	send_udp();
	return 0;
}

static void __exit ksock_udp_exit(void)
{
	pr_info("%s: unloaded\n", MODNAME);
}

module_init(ksock_udp_init);
module_exit(ksock_udp_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Nhom de tai 42 - L02 2026");
MODULE_DESCRIPTION("Bai 5: gui UDP tu kernel bang kernel_sendmsg");
MODULE_VERSION("1.0");
