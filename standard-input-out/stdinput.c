#include <stdio.h>
int main()
{
    char str[10];
    scanf("%s", str);
    fscanf(stdin,"%s", str);

    printf("%s\n", "hello");
    fprintf(stdout, "%s\n", "hello");
    return 0;
}
