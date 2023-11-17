
from enum import Enum
from typing import List, Optional, Dict

CLOCK = 0

class Operation(Enum):
    LOAD = "Load"
    SUB = "Sub"
    ADD = "Add"
    STORE = 'Store'


class UnitFunction(Enum):
    INTEGER = "Integer"
    MULT = "Mult"
    ADD = "Add"
    DIVIDE = "Divide"


class FloatRegister:
    def __init__(self, name: str) -> None:
        self.name = name
        self.ready_to_be_read = True  # 当前寄存器是否可以被读
        self.be_asked_to_read = 0  # 正在读当前寄存器的 unit 的数量 (用于 WAR) 的判断
        self.in_used_unit: Optional["Unit"] = None # 正在使用当前寄存器作为目的寄存器的 unit

    def __str__(self) -> str:
        return self.name

    def __format__(self, __format_spec: str) -> str:
        return format(self.name, __format_spec)


class Unit:
    def __init__(self, name: str, function: UnitFunction) -> None:
        self.name = name
        self.function = function
        self.instruction: Instruction = None

        self.usage_data: Dict[Instruction, List[int]] = {}

class RegisterGroup:
    def __init__(self) -> None:
        self.F0 = FloatRegister("F0")
        self.F2 = FloatRegister("F2")
        self.F4 = FloatRegister("F4")
        self.F6 = FloatRegister("F6")
        self.F8 = FloatRegister("F8")
        self.F10 = FloatRegister("F10")
        self.R2 = FloatRegister("R2")
        self.R3 = FloatRegister("R3")

        self.register_map = {
            "F0": self.F0,
            "F2": self.F2,
            "F4": self.F4,
            "F6": self.F6,
            "F8": self.F8,
            "F10": self.F10,
        }

    def __repr__(self) -> str:
        info = " " * 13
        reg_unit_tuples = []
        for name, reg in self.register_map.items():
            if reg.in_used_unit is not None:
                reg_unit_tuples.append((f"{name:<{len(reg.in_used_unit.name)}}", reg.in_used_unit.name))
            else:
                reg_unit_tuples.append((name, f'{" ":<{len(name)}}'))

        for name, _ in reg_unit_tuples:
            info += name + " "
        info += "\n"
        info += f"   Cycle {CLOCK:<2}  "
        for _, unit_name in reg_unit_tuples:
            info += unit_name + " "

        return info


class Instruction:
    ...

class Tomasulo:
    
    def __init__(self) -> None:
        self.instructions:List[Instruction] = None
        self.pc = 0

    def load_instructions(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.pc = 0

    def run(self):
        '''
        
        '''

def main():
    
    rg = RegisterGroup()

    # 做 3 组循环
    # lw      a4,0(a5)
    # fadd    a4,a4,a1
    # sw      a4,4(a5)
    # faddi   a5,a5,-4

    instructions = [
        Instruction(Op=Operation.LOAD, dest=rg.F6, j=34, k=rg.R2, latency=1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.ADD, dest=rg.F6, j=rg.F8, k=rg.F2, latency=2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.STORE, )
    ]
    loop_number = 3
    instructions = instructions * loop_number

    isa = Tomasulo()
    isa.load_instructions(instructions)
    isa.run()

if __name__ == "__main__":
    main()