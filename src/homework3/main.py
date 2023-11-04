from instructions import *
from isa import *


def main():
    # 汇编代码见 example.S

    #     xor a0, a0, a0
    #     lb a1, 0(a0)
    #     lb a2, 1(a0)
    # L1:
    #     addi a1, a1, 1
    #     addi a2, a2, 3
    #     bne a1, a2, L1
    #     jal a4, L2
    #     lb a5, 1(a0)
    #     lb a6, 1(a0)
    #     lb a7, 1(a0)
    # L2:
    #     sb a2, 3(a0)

    # 编译为 32 位 RISCV 目标文件

    # riscv64-linux-gnu-gcc -march=rv32i -mabi=ilp32 -c example.S -o example.o
    # riscv64-linux-gnu-objdump example.o -d

    instructions = [
        0x00000103,
        0x003100B3,
        0x40308233,
        0x0070F333,
        0x0090E433,
        0x00B0C533,
    ]

    isa = PipelineISA()
    # isa.registers[2] = 1
    isa.memory[0] = 1
    isa.registers[3] = 2
    isa.registers[7] = 10
    isa.registers[9] = 4
    isa.registers[11] = 3
    isa.load_instructions(instructions)
    isa.run()
    isa.show_info("after")


if __name__ == "__main__":
    main()
