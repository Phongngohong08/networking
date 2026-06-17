// SPDX-License-Identifier: GPL-2.0
/*
 * net_filter.c - Bai 2: Loc packet theo dia chi dich, cau hinh qua ioctl.
 *
 * Module tao mot misc device /dev/netfilter_ctl. User-space gui ioctl de
 * dat/xoa dia chi IP can chan. Netfilter hook se DROP moi goi co IP dich
 * trung gia tri da cau hinh.
 *
 * Dieu khien bang chuong trinh user-space: filter_ctl (xem filter_ctl.c).
 *
 * Tham khao: https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/skbuff.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/inet.h>

#define MODNAME "net_filter"

/* Dinh nghia lenh ioctl - phai khop voi user-space (filter_ctl.c) */
#define FILTER_IOC_MAGIC 'k'
#define FILTER_SET_ADDR  _IOW(FILTER_IOC_MAGIC, 1, __be32) /* dat IP can chan */
#define FILTER_CLR_ADDR  _IO(FILTER_IOC_MAGIC, 2)          /* xoa, ngung chan */

static __be32 blocked_addr;   /* 0 = khong chan gi */
static struct nf_hook_ops nfho;

/* ---- Netfilter hook: chan goi theo IP dich ---- */
static unsigned int hook_func(void *priv, struct sk_buff *skb,
			      const struct nf_hook_state *state)
{
	struct iphdr *iph;

	if (!skb || blocked_addr == 0)
		return NF_ACCEPT;

	iph = ip_hdr(skb);
	if (iph && iph->daddr == blocked_addr) {
		pr_info("%s: DROP goi den %pI4\n", MODNAME, &iph->daddr);
		return NF_DROP;
	}
	return NF_ACCEPT;
}

/* ---- Misc device: nhan cau hinh tu user-space qua ioctl ---- */
static long ctl_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
	__be32 addr;

	switch (cmd) {
	case FILTER_SET_ADDR:
		if (copy_from_user(&addr, (void __user *)arg, sizeof(addr)))
			return -EFAULT;
		blocked_addr = addr;
		pr_info("%s: dat IP can chan = %pI4\n", MODNAME, &blocked_addr);
		break;
	case FILTER_CLR_ADDR:
		blocked_addr = 0;
		pr_info("%s: da xoa cau hinh chan\n", MODNAME);
		break;
	default:
		return -ENOTTY;
	}
	return 0;
}

static const struct file_operations ctl_fops = {
	.owner          = THIS_MODULE,
	.unlocked_ioctl = ctl_ioctl,
};

static struct miscdevice ctl_dev = {
	.minor = MISC_DYNAMIC_MINOR,
	.name  = "netfilter_ctl",   /* tao /dev/netfilter_ctl */
	.fops  = &ctl_fops,
};

static int __init net_filter_init(void)
{
	int ret;

	ret = misc_register(&ctl_dev);
	if (ret) {
		pr_err("%s: misc_register that bai\n", MODNAME);
		return ret;
	}

	nfho.hook     = hook_func;
	nfho.hooknum  = NF_INET_LOCAL_OUT;  /* bắt gói đi RA từ máy này */
	nfho.pf       = PF_INET;
	nfho.priority = NF_IP_PRI_FIRST;
	nf_register_net_hook(&init_net, &nfho);

	pr_info("%s: loaded. Dieu khien qua /dev/netfilter_ctl\n", MODNAME);
	return 0;
}

static void __exit net_filter_exit(void)
{
	nf_unregister_net_hook(&init_net, &nfho);
	misc_deregister(&ctl_dev);
	pr_info("%s: unloaded\n", MODNAME);
}

module_init(net_filter_init);
module_exit(net_filter_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Nhom de tai 42 - L02 2026");
MODULE_DESCRIPTION("Bai 2: loc packet theo IP dich, cau hinh qua ioctl");
MODULE_VERSION("1.0");
