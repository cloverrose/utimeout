#include<stdlib.h>
#include<stdio.h>
#include<unistd.h>


unsigned long fib(int n)
{
    if(n == 0){
       return 0;
    }else if(n == 1){
        return 1;
    }else{
        return fib(n - 2) + fib(n - 1);
    }
}


int main(int argc, char* argv[])
{
    int n = atoi(argv[1]);
    printf("%lu\n", fib(n));
}
