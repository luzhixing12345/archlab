
from main import *

def main():
    rg = RegisterGroup()

    instructions = [
        # loop1
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
        # loop2
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
        # loop3
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
    ]

    isa = SuperScale(rg, multi_issue_number=2, cdb_number=2)
    
    new_unit = Unit(name="Address ALU", function=UnitFunction.INTEGER)
    isa.functional_units.append(new_unit)
    
    isa.load_instructions(instructions)
    isa.run()


if __name__ == "__main__":
    main()
