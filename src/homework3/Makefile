
file = loop.c

.PHONY: asm test

main:
	riscv64-linux-gnu-gcc -march=rv32i -mabi=ilp32 -Ofast -c $(file) -o example.o
	riscv64-linux-gnu-objdump example.o -d

asm:
	@riscv64-linux-gnu-gcc -march=rv32i -mabi=ilp32 -Ofast -c $(file) -o example.o
	@riscv64-linux-gnu-objdump example.o -d | awk '{print "0x" $$2 ","}'

test:
	python test.py