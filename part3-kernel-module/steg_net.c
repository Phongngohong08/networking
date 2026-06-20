/*
 * steg_net.c — Giấu tin trong gói TCP (Network Steganography)
 * Đề tài 42 — Lập trình nhân Linux, HVKTMM L02-2026
 *
 * Kỹ thuật: sử dụng trường IP Identification (16-bit) để mang
 *           từng byte của thông điệp bí mật.
 *
 *   Byte cao (bit 15-8) = 0xAB  ← magic, để nhận ra "gói steg"
 *   Byte thấp (bit  7-0) = ký tự thứ pos của secret
 *
 *   NF_INET_LOCAL_OUT   → EMBED: gói TCP ra ngoài tới peer_ip
 *   NF_INET_PRE_ROUTING → EXTRACT: gói TCP đến từ peer_ip
 *
 * Tham số nạp module:
 *   peer_ip  — địa chỉ IP đích/nguồn (bắt buộc)
 *   secret   — thông điệp cần giấu (default: "Hello from kernel!")
 *
 * Demo một VM (loopback):
 *   sudo insmod steg_net.ko peer_ip=127.0.0.1 'secret="HELLO"'
 *   Terminal 1: nc -l 7777
 *   Terminal 2: echo "test" | nc 127.0.0.1 7777
 *   Xem log: sudo dmesg | grep steg
 *            cat /proc/steg_net
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/inet.h>
#include <linux/in.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/atomic.h>
#include <linux/spinlock.h>
#include <net/checksum.h>
#include <net/ip.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Nhóm 42 — HVKTMM L02-2026");
MODULE_DESCRIPTION("Steganography: hide secret message in TCP packet IP ID field");

/* ---- Tham số module ---- */
static char *secret  = "Hello from kernel!";
static char *peer_ip = "";
module_param(secret,  charp, 0444);
module_param(peer_ip, charp, 0444);
MODULE_PARM_DESC(secret,  "Thông điệp cần giấu");
MODULE_PARM_DESC(peer_ip, "IP đích (embed) / IP nguồn (extract) — bắt buộc");

/* Byte cao của IP ID để đánh dấu gói steg */
#define STEG_MAGIC  0xAB

/* ---- Trạng thái toàn cục ---- */
static __be32      peer_addr;
static size_t      secret_len;
static atomic_t    embed_pos = ATOMIC_INIT(0);   /* vị trí ký tự tiếp theo */

#define EXTRACT_MAX 512
static char          extracted[EXTRACT_MAX];
static int           extract_pos;
static DEFINE_SPINLOCK(extract_lock);

/* =================================================================== */
/* EMBED — NF_INET_LOCAL_OUT                                           */
/* Mỗi gói TCP tới peer_ip → ghi 1 byte của secret vào IP ID          */
/* =================================================================== */
static unsigned int embed_hook(void *priv, struct sk_buff *skb,
			       const struct nf_hook_state *state)
{
	struct iphdr *iph;
	int  pos;
	u16  new_id;
	char ch;

	if (!skb || !peer_addr)
		return NF_ACCEPT;

	iph = ip_hdr(skb);
	if (!iph || iph->protocol != IPPROTO_TCP)
		return NF_ACCEPT;
	if (iph->daddr != peer_addr)
		return NF_ACCEPT;

	/* Lấy ký tự tiếp theo (vòng lặp khi hết secret) */
	pos = atomic_inc_return(&embed_pos) - 1;
	pos = pos % (int)secret_len;
	ch  = secret[pos];

	/* Ghi vào IP ID: byte cao = magic, byte thấp = ký tự */
	new_id     = ((u16)STEG_MAGIC << 8) | (u8)ch;
	iph->id    = htons(new_id);

	/* Tính lại IP checksum sau khi sửa header */
	iph->check = 0;
	iph->check = ip_fast_csum((u8 *)iph, iph->ihl);

	pr_info("steg [EMBED] pos=%2d  char='%c'(0x%02X)  IP_ID=0x%04X  -> %pI4\n",
		pos, ch, (u8)ch, new_id, &iph->daddr);

	return NF_ACCEPT;
}

/* =================================================================== */
/* EXTRACT — NF_INET_PRE_ROUTING                                       */
/* Gói TCP đến từ peer_ip → đọc byte ẩn trong IP ID                   */
/* =================================================================== */
static unsigned int extract_hook(void *priv, struct sk_buff *skb,
				 const struct nf_hook_state *state)
{
	struct iphdr *iph;
	u16 ip_id;
	u8  magic, ch;

	if (!skb || !peer_addr)
		return NF_ACCEPT;

	iph = ip_hdr(skb);
	if (!iph || iph->protocol != IPPROTO_TCP)
		return NF_ACCEPT;
	if (iph->saddr != peer_addr)
		return NF_ACCEPT;

	ip_id = ntohs(iph->id);
	magic = (ip_id >> 8) & 0xFF;
	ch    =  ip_id       & 0xFF;

	/* Chỉ xử lý gói có magic đúng */
	if (magic != STEG_MAGIC)
		return NF_ACCEPT;

	pr_info("steg [EXTRACT] IP_ID=0x%04X  magic=0x%02X  char='%c'(0x%02X)  from %pI4\n",
		ip_id, magic, ch, ch, &iph->saddr);

	spin_lock(&extract_lock);
	if (extract_pos < EXTRACT_MAX - 1) {
		extracted[extract_pos++] = ch;
		extracted[extract_pos]   = '\0';
	}
	spin_unlock(&extract_lock);

	return NF_ACCEPT;
}

/* =================================================================== */
/* /proc/steg_net — xem trạng thái                                     */
/* =================================================================== */
static int steg_show(struct seq_file *m, void *v)
{
	int pos = atomic_read(&embed_pos) % (int)secret_len;

	seq_printf(m, "=== steg_net status ===\n");
	seq_printf(m, "secret      : \"%s\" (%zu bytes)\n", secret, secret_len);
	seq_printf(m, "peer_ip     : %s (%pI4)\n", peer_ip, &peer_addr);
	seq_printf(m, "magic       : 0x%02X (IP ID byte cao)\n", STEG_MAGIC);
	seq_printf(m, "embed_pos   : %d (ký tự tiếp theo: '%c')\n",
		   pos, secret[pos]);
	spin_lock(&extract_lock);
	seq_printf(m, "extracted   : \"%s\" (%d bytes)\n", extracted, extract_pos);
	spin_unlock(&extract_lock);
	return 0;
}

static int steg_open(struct inode *inode, struct file *file)
{
	return single_open(file, steg_show, NULL);
}

static const struct proc_ops steg_proc_ops = {
	.proc_open    = steg_open,
	.proc_read    = seq_read,
	.proc_lseek   = seq_lseek,
	.proc_release = single_release,
};

/* ---- Netfilter hooks ---- */
static struct nf_hook_ops embed_ops = {
	.hook     = embed_hook,
	.pf       = PF_INET,
	.hooknum  = NF_INET_LOCAL_OUT,
	.priority = NF_IP_PRI_FIRST,
};

static struct nf_hook_ops extract_ops = {
	.hook     = extract_hook,
	.pf       = PF_INET,
	.hooknum  = NF_INET_PRE_ROUTING,
	.priority = NF_IP_PRI_FIRST,
};

/* =================================================================== */
/* Init / Exit                                                          */
/* =================================================================== */
static int __init steg_init(void)
{
	int ret;

	if (!peer_ip || !*peer_ip) {
		pr_err("steg_net: thiếu tham số peer_ip (vd: peer_ip=192.168.1.100)\n");
		return -EINVAL;
	}
	if (in4_pton(peer_ip, -1, (u8 *)&peer_addr, -1, NULL) != 1) {
		pr_err("steg_net: peer_ip không hợp lệ: '%s'\n", peer_ip);
		return -EINVAL;
	}

	secret_len = strlen(secret);
	if (secret_len == 0) {
		pr_err("steg_net: secret không được rỗng\n");
		return -EINVAL;
	}

	ret = nf_register_net_hook(&init_net, &embed_ops);
	if (ret) {
		pr_err("steg_net: đăng ký embed hook thất bại (%d)\n", ret);
		return ret;
	}

	ret = nf_register_net_hook(&init_net, &extract_ops);
	if (ret) {
		pr_err("steg_net: đăng ký extract hook thất bại (%d)\n", ret);
		nf_unregister_net_hook(&init_net, &embed_ops);
		return ret;
	}

	proc_create("steg_net", 0444, NULL, &steg_proc_ops);

	pr_info("steg_net: nạp xong — secret=\"%s\" peer=%pI4\n",
		secret, &peer_addr);
	pr_info("steg_net: EMBED @ LOCAL_OUT | EXTRACT @ PRE_ROUTING\n");
	pr_info("steg_net: theo dõi: sudo dmesg -w | grep steg\n");
	pr_info("steg_net: trạng thái: cat /proc/steg_net\n");
	return 0;
}

static void __exit steg_exit(void)
{
	remove_proc_entry("steg_net", NULL);
	nf_unregister_net_hook(&init_net, &extract_ops);
	nf_unregister_net_hook(&init_net, &embed_ops);
	pr_info("steg_net: gỡ module. Đã trích xuất: \"%s\"\n", extracted);
}

module_init(steg_init);
module_exit(steg_exit);
