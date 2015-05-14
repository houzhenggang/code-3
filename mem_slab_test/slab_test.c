/*
 * Module is used to drop packets for AppEx's Test. 
 */
#include <linux/module.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/version.h>
#include <linux/skbuff.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/moduleparam.h>
#include <linux/slab.h>
#include<linux/cache.h>

static struct kmem_cache *my_cachep;

static void init_my_cache(void)
{
	
		my_cachep = kmem_cache_create(
						"my_create",
						32,
						0,
						SLAB_HWCACHE_ALIGN,
						NULL);

		printk("Cache alloc\n");
		return;
}

int slab_test(void)
{
		void *object;

	//	printk("Cache name is %s\n", kmem_cache_name(my_cachep));
	//	printk("Cache object size is %d\n", kmem_cache_size(my_cachep));

		object = kmem_cache_alloc(my_cachep, GFP_KERNEL);

		if(object)
		{
				kmem_cache_free(my_cachep, object);
		}
		return 0;
}

static void remove_my_cache(void)
{
		if(my_cachep) kmem_cache_destroy(my_cachep);
		
		printk("Cache free\n");
		return;
}

static int __init __slab_test_init(void)
{
	init_my_cache();
	slab_test();
	return 0;
}

static void __exit __slab_test_exit(void)
{
	remove_my_cache();
}

module_init(__slab_test_init);
module_exit(__slab_test_exit);

