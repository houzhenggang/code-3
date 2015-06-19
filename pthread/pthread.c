#include <pthread.h>
#include <stdio.h>
#include <string.h>
void *route(void*   args)
{
	int *iptr = ((void**)args)[0];
	float *fptr = ((void**)args)[1];
	char* str =((void**)args)[2];
	printf("integer:  %d \nfloat: %f\n string: %s\n",*iptr,*fptr,str);
	return   0;
}

int main(void)
{
pthread_t thr_id;
int  ival =  1;
float   fval   =   10.0F;
char   buf[]   =   "func";
void*   arg[3]={&ival,   &fval,   buf};
pthread_create(&thr_id,   NULL,   route,   arg);
sleep(1);
}
