# 

add x1, x2, x3
sub x4, x1, x3
and x6, x1, x7
or x8, x1, x9
xor x10, x1, x11

// 0x003100b3,
// 0x40308233,
// 0x0070f333,
// 0x0090e433,
// 0x00b0c533,

// isa.registers[2] = 1
// isa.registers[3] = 2
// isa.registers[7] = 10
// isa.registers[9] = 4
// isa.registers[11] = 3

// r0  =   0 |r1  =   3 |r2  =   1 |r3  =   2 |r4  =   1 |r5  =   0 |r6  =   2 |r7  =  10 |
// r8  =   7 |r9  =   4 |r10 =   0 |r11 =   3 |r12 =   0 |r13 =   0 |r14 =   0 |r15 =   0 |
// r16 =   0 |r17 =   0 |r18 =   0 |r19 =   0 |r20 =   0 |r21 =   0 |r22 =   0 |r23 =   0 |
// r24 =   0 |r25 =   0 |r26 =   0 |r27 =   0 |r28 =   0 |r29 =   0 |r30 =   0 |r31 =   0 |