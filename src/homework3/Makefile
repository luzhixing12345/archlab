
file = example.S

run:
	python main.py

main:
	riscv64-linux-gnu-gcc -march=rv32i -mabi=ilp32 -O0 -c example.c -o example.o
	riscv64-linux-gnu-objdump example.o -d

asm:
	@riscv64-linux-gnu-gcc -march=rv32i -mabi=ilp32 -O0 -c $(file) -o example.o
	@riscv64-linux-gnu-objdump example.o -d | awk '{print "0x" $$2 ","}'