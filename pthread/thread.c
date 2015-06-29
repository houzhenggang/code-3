#include <pthread.h>
#include <stdio.h>

    pthread_cond_t qready = PTHREAD_COND_INITIALIZER;    //初始构造条件变量
    pthread_mutex_t qlock = PTHREAD_MUTEX_INITIALIZER;    //初始构造锁
    pthread_t tid1,tid2,tid3;

    int x = 10;
    int y = 20;

    void *thrd_1(void *arg)
    {
        pthread_mutex_lock(&qlock);
        while(x<y)
        {
            pthread_cond_wait(&qready,&qlock);
        }
        pthread_mutex_unlock(&qlock);
        printf("1\n");
        sleep(5);
    }

    void *thrd_2(void *arg)
    {
        pthread_mutex_lock(&qlock);
        x = 20;
        y = 10;
        printf("has change x and y\n");


        pthread_mutex_unlock(&qlock);
        if(x > y)
        {
            pthread_cond_signal(&qready);
        }
        printf("2\n");
    }

    void *thrd_3(void *arg)
    {
        pthread_join(tid1,NULL);
        printf("3\n");
    }

    int main(int argc,char **argv)
    {
        int err;
        err = pthread_create(&tid1,NULL,thrd_1,NULL);
        if(err != 0)
        {
            printf("pthread 1 create error\n");
        }
        err = pthread_create(&tid2,NULL,thrd_2,NULL);
        if(err != 0)
        {
            printf("pthread 2 create error\n");
        }
        err = pthread_create(&tid3,NULL,thrd_3,NULL);
        if(err != 0)
        {
            printf("pthread 3 create error\n");
        }
        while(1)
        {
            sleep(1);
        }
        return 0;
        
    }
