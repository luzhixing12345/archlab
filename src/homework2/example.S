xor a0, a0, a0
lb a1, 0(a0)
lb a2, 1(a0)
L1:
addi a1, a1, 1
addi a2, a2, 3
bne a1, a2, L1
jal a4, L2
L2:
sb a2, 3(a0)