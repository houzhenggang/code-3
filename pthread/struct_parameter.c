#include <pthread.h>
#include <stdio.h>
#include <string.h>

typedef struct{
    int a;
    float b;
    char buf[10];
}info;
void *route(void*   args)
{

    info *temp = (info*)args;
    int a = temp->a;
    temp->a ++;
    float b = temp->b;
    char buff[10];
    strcpy(buff,temp->buf);
    printf("integer:  %d \nfloat: %f\n string: %s\n",a,b,buff);
    return   0;
}

int main(void)
{
    pthread_t thr_id;
    info info1;
    info1.a =1 ;
    info1.b =10.0F;
    strcpy(info1.buf, "fun");

    pthread_create(&thr_id,   NULL,   route,   (void*)&info1);
    sleep(3);
    printf("integer:  %d \nfloat: %f\n string: %s\n",info1.a,info1.b,info1.buf);
    sleep(1);
}
