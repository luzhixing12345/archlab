
# lab4

1.设计一种机制,并在你的模拟器中实现,使得下述代码结果正确.
要求:不能改动下面的代码.

```c
void main()
{
    int N=64, i, sum=0;
    #pragma omp parallel for
    for (i=0; i<N; i++)
        sum += i;
    printf( "sum = %d\n", sum );
}
```