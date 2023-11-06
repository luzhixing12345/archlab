from instructions import *
from isa import *


def main():

    # 00000000 <loop_test>:
    #  0:   18c50793                addi    a5,a0,396

    # 00000004 <.L2>:
    #  4:   0007a703                lw      a4,0(a5)
    #  8:   00078693                mv      a3,a5
    #  c:   ffc78793                addi    a5,a5,-4
    # 10:   00b70733                add     a4,a4,a1
    # 14:   00e7a223                sw      a4,4(a5)
    # 18:   fed516e3                bne     a0,a3,4 <.L2>
    # 1c:   00008067                ret
    instructions = [
        0x18C50793,
        0x0007A703,
        0x00078693,
        0xFFC78793,
        0x00B70733,
        0x00E7A223,
        0xFED516E3,
        0x00008067,
    ]

    isa = PipelineISA()
    isa.registers[10] = 0x200
    isa.registers[11] = 4

    isa.load_instructions(instructions)
    isa.run()
    isa.show_info("after")


if __name__ == "__main__":
    main()
