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
        0x00A54533,
        0x00050583,
        0x00150603,
        0x00158593,
        0x00360613,
        0xFEC59CE3,
        0x0100076F,
        0x00150783,
        0x00150803,
        0x00150883,
        0x00C501A3,
    ]

    isa = PipelineISA()
    isa.memory[0] = 20
    isa.memory[1] = 0
    isa.load_instructions(instructions)
    isa.run()
    isa.show_info("after")


if __name__ == "__main__":
    main()
