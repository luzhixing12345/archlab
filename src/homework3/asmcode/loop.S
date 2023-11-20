
// void loop_test(int *x, int s) {
    
//     for (int i = 999; i >= 0; i--) {
//         x[i] = x[i] + s;
//     }
// }

    lui     a5,0x1
    addi    a5,a5,-100 # f9c <.L2+0xf90>
    add     a5,a0,a5

L2:
    lw      a4,0(a5)
    nop
    add     a4,a4,a1
    nop
    nop
    sw      a4,0(a5)
    addi    a5,a5,-4
    nop
    bne     a0,a5, L2
    ret