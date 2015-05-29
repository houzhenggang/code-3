#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/sched.h>
#include <linux/mm.h>
  
#define MODULE_NAME "Memory"
  
int my_read_proc(char *page,char **start, off_t off,int count,  int *eof,void *data)
{
        struct task_struct *tsk = current;
        int len;
        len = sprintf( page, "This module info: task %s pid %d\n",tsk->comm, tsk->pid );
        return  len;
}
  
struct proc_dir_entry *proc_entry;

int init_module(void)
{
        proc_entry = create_proc_entry(MODULE_NAME, 0644, NULL);
        if (proc_entry==NULL){
                remove_proc_entry(MODULE_NAME, NULL);
        }
        proc_entry->read_proc = my_read_proc;
        return  0;
}
  
void cleanup_module(void)
{
        remove_proc_entry(MODULE_NAME, NULL); // 退出和出错记的删除
}
  
MODULE_LICENSE("GPL");
