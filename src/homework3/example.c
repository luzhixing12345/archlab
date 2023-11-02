
void loop_test(int *x, int n) {
    int i;
    int s = 4;
    for (i = 999; i >= n; i--) {
        x[i] = x[i] + s;
    }
}