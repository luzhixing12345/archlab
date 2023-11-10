
void loop_test(int *x, int s) {
    
    for (int i = 999; i >= 0; i--) {
        x[i] = x[i] + s;
    }
}