#include<unistd.h>
#define SIZE 100
int main(void)
{
int n;\
char buf[SIZE];
while(n=read(STDIN_FILENO,buf,SIZE))   //读取标准输入到buf中，返回读取字节数。
{
if(n!=write(STDOUT_FILENO,buf,n))
perror("write error");
}if(n<0) 
perror("read error");
return 0;
}
