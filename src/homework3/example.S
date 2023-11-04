xor a0, a0, a0
lb a1, 0(a0)
lb a2, 1(a0)
addi a2, a2, 1
sb a2, 3(a0)
addi a3, a1, 1
add a4, a2, a3
sb a4, 5(a0)
