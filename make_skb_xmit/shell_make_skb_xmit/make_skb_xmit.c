#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netfilter.h>
#include <linux/skbuff.h>
#include <linux/ip.h>
#include <linux/inet.h>
#include <linux/netdevice.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <net/tcp.h>
#include <net/udp.h>
#include <net/route.h>
#include <net/icmp.h>
#include <linux/netfilter_ipv4.h>
 
MODULE_LICENSE("GPL");
MODULE_AUTHOR("kenthy@163.com");

/*#define    ETH     "eth0"
#define    SIP     "192.168.238.180"
#define    DIP     "192.168.1.101"
#define    SPORT   39804
#define    DPORT   80*/
static uint SPORT = 39804;
static uint DPORT = 80;
static char* SIP = "10.216.25.45";
static char* DIP = "10.216.25.44";
static char* ETH = "eth0";

module_param(SPORT, uint, 0);
module_param(DPORT, uint, 0);
module_param(SIP, charp, 0);
module_param(DIP, charp, 0);
module_param(ETH, charp, 0);


unsigned char   SMAC[ETH_ALEN] = {0x90,0xB1,0x1C,0x2A,0xF7,0xC1};
unsigned char   DMAC[ETH_ALEN] = {0x90,0xB1,0x1C,0x30,0xDC,0xF9};

int cp_dev_xmit_tcp (char * eth, u_char * smac, u_char * dmac,
             u_char * pkt, int pkt_len, 
             u_long sip, u_long dip, 
             u_short sport, u_short dport, u_long seq, u_long ack_seq, u_char psh, u_char fin)
{
    struct sk_buff * skb = NULL;
    struct net_device * dev = NULL;
    struct ethhdr * ethdr = NULL;
    struct iphdr * iph = NULL;
    struct tcphdr * tcph = NULL;
    u_char * pdata = NULL;
    int nret = 1;
    if (NULL == smac || NULL == dmac) goto out;
    dev = dev_get_by_name(&init_net, eth);
    if (NULL == dev) 
        goto out;
    skb = alloc_skb (pkt_len + sizeof (struct iphdr) + sizeof (struct tcphdr) + LL_RESERVED_SPACE (dev), GFP_ATOMIC);
    /*  
    LL_RESERVED_SPACE(dev) = 16
    alloc_skb返回以后，skb->head = skb_data = skb->tail =  alloc_skb分配的内存区首地址,skb->len = 0;
    skb->end = skb->tail + size;
         注：我的机子是32位x86机器，所以没有定义NET_SKBUFF_DATA_USES_OFFSET，因而，
     skb->tail,skb->mac_header,skb->network_header,skb->transport_header这几个成员都是指针
    */
      if (NULL == skb) 
            goto out;
    skb_reserve (skb, LL_RESERVED_SPACE (dev));//add data and tail
    skb->dev = dev;
    skb->pkt_type = PACKET_OTHERHOST;
    skb->protocol = __constant_htons(ETH_P_IP);
    skb->ip_summed = CHECKSUM_NONE;
    skb->priority = 0;
    //skb->nh.iph = (struct iphdr*)skb_put(skb, sizeof (struct iphdr));
    //skb->h.th = (struct tcphdr*)skb_put(skb, sizeof (struct tcphdr));
    skb_set_network_header(skb, 0);    //skb->network_header = skb->data + 0;
    skb_put(skb, sizeof (struct iphdr)); //add tail and len
    skb_set_transport_header(skb, sizeof (struct iphdr));//skb->transport_header = skb->data + sizeof (struct iphdr)
    skb_put(skb, sizeof (struct tcphdr));    
    pdata = skb_put (skb, pkt_len); 
      {
            if (NULL != pkt) 
                 memcpy (pdata, pkt, pkt_len);
      }

    {
        tcph = tcp_hdr(skb);
        memset (tcph, 0, sizeof (struct tcphdr));
        tcph->source = sport;
        tcph->dest = dport;
        tcph->seq = seq;
        tcph->ack_seq = ack_seq;
        tcph->doff = 5;
        tcph->psh = psh;
        tcph->fin = fin;
        tcph->syn = 1;
        tcph->ack = 0;
        tcph->window = __constant_htons (5840);
        skb->csum = 0;
        tcph->check = 0;
    }

    {
        iph = ip_hdr(skb);
        iph->version = 4;
        iph->ihl = sizeof(struct iphdr)>>2;
        iph->frag_off = 0;
        iph->protocol = IPPROTO_TCP;
        iph->tos = 0;
        iph->daddr = dip;
        iph->saddr = sip;
        iph->ttl = 0x40;
        iph->tot_len = __constant_htons(skb->len);
        iph->check = 0;
    }
      skb->csum = skb_checksum (skb, iph->ihl*4, skb->len - iph->ihl * 4, 0);
    tcph->check = csum_tcpudp_magic (sip, dip, skb->len - iph->ihl * 4, IPPROTO_TCP, skb->csum);
    { 
        ethdr = (struct ethhdr*)skb_push (skb, 14);//reduce data and add len
        memcpy (ethdr->h_dest, dmac, ETH_ALEN);
        memcpy (ethdr->h_source, smac, ETH_ALEN);
        ethdr->h_proto = __constant_htons (ETH_P_IP);
    }
     if (0 > dev_queue_xmit(skb)) goto out;
    nret = 0;
out:
    if (0 != nret && NULL != skb) 
    {
        dev_put (dev); 
        kfree_skb (skb);
    }
      return (nret);
}

static int __init init(void)
{
    printk("%s\n","insmod skb_diy module\n");
        cp_dev_xmit_tcp (ETH, SMAC, DMAC,NULL, 0, 
                    in_aton(SIP),in_aton(DIP),
                    htons(SPORT),htons(DPORT),
                    0, 0, 0, 0);
    return 0;
}

static void __exit fini(void)
{
    printk("%s\n","remove skb_diy module.\n");
}

module_init(init);
module_exit(fini);
