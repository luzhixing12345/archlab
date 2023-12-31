xor x0, x0, x0      # x0 = 0
lb x1, 0(x0)        # x1 = 100
lb x2, 1(x0)        # x2 = 200
addi x2, x2, 1      # x2 = 200 + 1 = 201
sb x2, 3(x0)        # mem[3] = 201
addi x3, x1, 1      # x3 = 100 + 1 = 101
add x4, x2, x3      # x4 = 201 + 101 = 302
sb x4, 5(x0)        # mem[5] = 302

// 0x00004033,
// 0x00000083,
// 0x00100103,
// 0x00110113,
// 0x002001a3,
// 0x00108193,
// 0x00310233,
// 0x004002a3,

// isx.memory[0] = 100
// isx.memory[1] = 200

// mem[ 0] = 100 |mem[ 1] = 200 |mem[ 2] =   0 |mem[ 3] = 201 |
// mem[ 4] =   0 |mem[ 5] = 302 |mem[ 6] =   0 |mem[ 7] =   0 |
// mem[ 8] =   0 |mem[ 9] =   0 |mem[10] =   0 |mem[11] =   0 |
// mem[12] =   0 |mem[13] =   0 |mem[14] =   0 |mem[15] =   0 |
// mem[16] =   0 |mem[17] =   0 |mem[18] =   0 |mem[19] =   0 |
// --------------------
// r0  =   0 |r1  = 100 |r2  = 201 |r3  = 101 |r4  = 302 |r5  =   0 |r6  =   0 |r7  =   0 |
// r8  =   0 |r9  =   0 |r10 =   0 |r11 =   0 |r12 =   0 |r13 =   0 |r14 =   0 |r15 =   0 |
// r16 =   0 |r17 =   0 |r18 =   0 |r19 =   0 |r20 =   0 |r21 =   0 |r22 =   0 |r23 =   0 |
// r24 =   0 |r25 =   0 |r26 =   0 |r27 =   0 |r28 =   0 |r29 =   0 |r30 =   0 |r31 =   0 |
