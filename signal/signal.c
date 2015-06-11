#include <signal.h>
#include <stdio.h>

int cnt = 0;

void cbSignalAlarm(int signo)
{
	printf("second : %d\n", ++cnt);
	alarm(1);
}

void main()
{
	signal(SIGALRM,cbSignalAlarm);
	setbuf(stdout,NULL);
	
	alarm(1);
	
	while(1)
		pause();
}
  
