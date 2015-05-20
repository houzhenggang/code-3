#include<stdio.h>
char (*pFun)(int);
char glFun(int a){printf("a =%d\n",a);return a;}
void main()
{
		pFun = glFun;
		char temp =(*pFun)(2);
		printf("temp =%d\n",temp);

}
