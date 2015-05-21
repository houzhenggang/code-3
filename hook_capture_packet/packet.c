#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netfilter.h>
#include <linux/skbuff.h>
#include <linux/ip.h>
#include <linux/netdevice.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <net/tcp.h>
#include <net/udp.h>
#include <net/icmp.h>
#include <linux/netfilter_ipv4.h>

#define MAC_FMT "%02x:%02x:%02x:%02x:%02x:%02x"
#define MAC_ARG(x) ((u8*)(x))[0],((u8*)(x))[1],((u8*)(x))[2],((u8*)(x))[3],((u8*)(x))[4],((u8*)(x))[5]

MODULE_LICENSE("GPL");
MODULE_AUTHOR("kenthy@163.com");

const char* hooks[] ={ "NF_IP_PRE_ROUTING",
                             "NF_IP_LOCAL_IN",
                             "NF_IP_FORWARD",
                             "NF_IP_LOCAL_OUT",
                             "NF_IP_POST_ROUTING"};

void print_ipproto(int proto)
{
 switch(proto)
 {
         case IPPROTO_ICMP:
                 printk("%s\n", "IPPROTO_ICMP");
           break;
         case IPPROTO_TCP:
                 printk("%s\n", "IPPROTO_TCP");
           break;
         case IPPROTO_UDP:
                 printk("%s\n", "IPPROTO_UDP");
           break;
         default:
                 printk("%s\n", "other IPPROTO");
         }
}

void print_mac_test(struct ethhdr* eth)
{
 if(eth==NULL)
         return;
         
 if(eth->h_source!=NULL)
        printk("SOURCE:" MAC_FMT "\n", MAC_ARG(eth->h_source));

 if(eth->h_dest!=NULL)
             printk("DEST:" MAC_FMT "\n", MAC_ARG(eth->h_dest));
}

unsigned int mac(unsigned int hooknum,
                 struct sk_buff* skb,
                 const struct net_device *in,
                 const struct net_device *out,
                 int (*okfn)(struct sk_buff*))
{
   struct sk_buff* nskb;
   struct iphdr *iph = NULL;
   struct ethhdr* eth;
  
  nskb = skb;
  if(nskb==NULL)
  {
    printk("%s\n", "*skb is NULL");
    return NF_ACCEPT;
   }
  
  iph = ip_hdr(nskb);
  if(iph == NULL)
  {
    printk("%s\n", "*iph is NULL");
    return NF_ACCEPT;
   }

      
   printk("------begin %s--------\n", hooks[hooknum]);
   print_ipproto(iph->protocol);
   printk("len is %d, data len is %d\n", nskb->len, nskb->data_len);
   if(nskb->mac_len > 0)
           {
            eth = (struct ethhdr*)skb_mac_header(nskb);
            print_mac_test(eth);        
                   }
   else
    printk("%s", "mac is NULL");                
    
    
   printk("------end  %s--------\n", hooks[hooknum]);
  
    return NF_ACCEPT;
}

/* Register to Kernel, support Local_in and Local_out now! */
static struct nf_hook_ops mac_ops[] __read_mostly = {
	{
		.hook           = mac,
		.owner          = THIS_MODULE,
		.pf             = PF_INET,
		.hooknum        = NF_INET_LOCAL_IN,
		.priority       = NF_IP_PRI_FIRST,
	},
	{
		.hook           = mac,
		.owner          = THIS_MODULE,
		.pf             = PF_INET,
		.hooknum        = NF_INET_LOCAL_OUT,
		.priority       = NF_IP_PRI_FIRST,
	}
};



static int __init __mac_init(void)
{
    int ret;
    ret = nf_register_hooks(mac_ops, ARRAY_SIZE(mac_ops));
    if (ret < 0) {
        printk("http detect:can't register mac_ops detect hook!\n");
        return ret;
    }
    printk("insmod mac_ops detect module\n");
    return 0;
}

static void __exit __mac_fini(void)
{
    nf_unregister_hooks(mac_ops, ARRAY_SIZE(mac_ops));
    printk("remove mac_ops detect module.\n");
}

module_init(__mac_init);
module_exit(__mac_fini);
