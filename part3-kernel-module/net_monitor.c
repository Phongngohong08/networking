// SPDX-License-Identifier: GPL-2.0
/*
 * net_monitor.c - Đề tài 42 (Networking)
 *
 * Kernel module dùng netfilter hook để giám sát các gói tin đi vào máy.
 * Với mỗi gói IP, module in ra dmesg: giao thức, IP nguồn -> IP đích,
 * và (với TCP/UDP) cổng nguồn/đích cùng các cờ TCP.
 *
 * Tham khảo: https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html
 *
 * Build:  make
 * Nạp:    sudo insmod net_monitor.ko
 * Xem:    sudo dmesg -w
 * Gỡ:     sudo rmmod net_monitor
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/skbuff.h>
#include <linux/inet.h>

#define MODNAME "net_monitor"

/* struct lưu cấu hình netfilter hook */
static struct nf_hook_ops nfho;

/*
 * Hàm callback được gọi cho mỗi gói tin tại điểm hook.
 * Trả về NF_ACCEPT để cho gói đi tiếp (không chặn).
 */
static unsigned int hook_func(void *priv,
			      struct sk_buff *skb,
			      const struct nf_hook_state *state)
{
	struct iphdr *iph;
	struct tcphdr *tcph;
	struct udphdr *udph;

	if (!skb)
		return NF_ACCEPT;

	iph = ip_hdr(skb);
	if (!iph)
		return NF_ACCEPT;

	switch (iph->protocol) {
	case IPPROTO_TCP:
		tcph = tcp_hdr(skb);
		pr_info("%s: TCP %pI4:%u -> %pI4:%u [%s%s%s%s]\n",
			MODNAME,
			&iph->saddr, ntohs(tcph->source),
			&iph->daddr, ntohs(tcph->dest),
			tcph->syn ? "SYN " : "",
			tcph->ack ? "ACK " : "",
			tcph->fin ? "FIN " : "",
			tcph->rst ? "RST" : "");
		break;
	case IPPROTO_UDP:
		udph = udp_hdr(skb);
		pr_info("%s: UDP %pI4:%u -> %pI4:%u\n",
			MODNAME,
			&iph->saddr, ntohs(udph->source),
			&iph->daddr, ntohs(udph->dest));
		break;
	case IPPROTO_ICMP:
		pr_info("%s: ICMP %pI4 -> %pI4\n",
			MODNAME, &iph->saddr, &iph->daddr);
		break;
	default:
		pr_info("%s: IP proto=%u %pI4 -> %pI4\n",
			MODNAME, iph->protocol, &iph->saddr, &iph->daddr);
		break;
	}

	return NF_ACCEPT;
}

static int __init net_monitor_init(void)
{
	nfho.hook     = hook_func;
	nfho.hooknum  = NF_INET_PRE_ROUTING;   /* bắt gói ngay khi vừa vào */
	nfho.pf       = PF_INET;
	nfho.priority = NF_IP_PRI_FIRST;

	nf_register_net_hook(&init_net, &nfho);

	pr_info("%s: loaded - dang giam sat goi tin\n", MODNAME);
	return 0;
}

static void __exit net_monitor_exit(void)
{
	nf_unregister_net_hook(&init_net, &nfho);
	pr_info("%s: unloaded\n", MODNAME);
}

module_init(net_monitor_init);
module_exit(net_monitor_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Nhom de tai 42 - L02 2026");
MODULE_DESCRIPTION("Netfilter hook giam sat packet (TCP/UDP/ICMP)");
MODULE_VERSION("1.0");
