#include <stdio.h>
#include <string.h>

int is_brother(char *a , char *b)
{
    int flag = 0;
    int i;

    if (strlen(a) != strlen(b))
        return 0;

    for ( i = 0; i< strlen(a); i++ ) {
        flag |= (1 << (*(a + i) - 'A'));
    }

    for ( i = 0; i < strlen(b); i++ ) {
        if( (flag & (1 << (*(b +i) - 'A'))) == 0)
            return 0;
    }

    return 1;
}
int stringcontain(char *a_long, char *b_short)
{
    int flag = 0;
    int i;
    for ( i = 0; i< strlen(a_long); i++ ) {
        flag |= (1 << (*(a_long + i) - 'A'));
    }

    for ( i = 0; i < strlen(b_short); i++ ) {
        if( (flag & (1 << (*(b_short +i) - 'A'))) == 0)
            return 0;
    }

    return 1;

}

int main( int argc, char **argv )
{
    char *stra = "abc";
    char *strb = "bca";
    char *strc = "rfdabcgg";
    char *strd = "bca";

    printf( "1 == True \n 0 == Flse \n" );
    printf( "stra and strb is_brother = %d\n", is_brother(stra, strb) );
    printf( "strc contain std = %d\n", stringcontain(strc,strd) );

    return 0;
}
