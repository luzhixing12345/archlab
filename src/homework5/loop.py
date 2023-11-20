from main import *


def main():
    rg = RegisterGroup()
    rg.R2.value = 200

    # lw       a0,0(R2)
    # fadd     a2,a0,R3
    # sw       a2,0(R2)

    # lw       a4,-4(R2)
    # fadd     a6,a4,R3
    # sw       a6,-4(R2)

    # lw       a8,-8(R2)
    # fadd     a10,a8,R3
    # sw       a10,-8(R2)

    instructions = [
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R2, latency=1, unit_function=UnitFunction.LOAD),
        Instruction(Op=Operation.ADD, dest=rg.F2, j=rg.F0, k=rg.R3, latency=2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.STORE, dest=rg.F2, j=0, k=rg.R2, latency=1, unit_function=UnitFunction.STORE),
        Instruction(Op=Operation.LOAD, dest=rg.F4, j=-4, k=rg.R2, latency=1, unit_function=UnitFunction.LOAD),
        Instruction(Op=Operation.ADD, dest=rg.F6, j=rg.F4, k=rg.R3, latency=2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.STORE, dest=rg.F6, j=-4, k=rg.R2, latency=1, unit_function=UnitFunction.STORE),
        Instruction(Op=Operation.LOAD, dest=rg.F8, j=-8, k=rg.R2, latency=1, unit_function=UnitFunction.LOAD),
        Instruction(Op=Operation.ADD, dest=rg.F10, j=rg.F8, k=rg.R3, latency=2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.STORE, dest=rg.F10, j=-8, k=rg.R2, latency=1, unit_function=UnitFunction.STORE),
    ]

    isa = Tomasulo(rg)
    isa.load_instructions(instructions)
    isa.run()


if __name__ == "__main__":
    main()
