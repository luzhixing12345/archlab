from enum import Enum
from typing import List, Dict, Union, Optional

CLOCK = 0


class Operation(Enum):
    LOAD = "Load"
    STORE = "Store"
    SUB = "Sub"
    ADD = "Add"
    FADD = "Fadd"
    BNE = "Bne"


class UnitFunction(Enum):
    INTEGER = "Integer"
    ADD = "Add"
    FADD = "Fadd"
    BRANCH = "Branch"


class FloatRegister:
    def __init__(self, name: str) -> None:
        self.name = name
        self.value = 0
        self.in_used_unit: Optional["Unit"] = None  # 正在使用当前寄存器作为目的寄存器的 unit

    def __str__(self) -> str:
        return self.name

    def __format__(self, __format_spec: str) -> str:
        return format(self.name, __format_spec)


class RegisterGroup:
    def __init__(self) -> None:
        self.F0 = FloatRegister("F0")
        self.F2 = FloatRegister("F2")
        self.F4 = FloatRegister("F4")
        self.F6 = FloatRegister("F6")
        self.F8 = FloatRegister("F8")
        self.F10 = FloatRegister("F10")
        self.R1 = FloatRegister("R1")
        self.R2 = FloatRegister("R2")

        self.register_map = {
            "F0": self.F0,
            "F2": self.F2,
            "F4": self.F4,
            "F6": self.F6,
            "F8": self.F8,
            "F10": self.F10,
        }


class UnitState:
    def __init__(self) -> None:
        self.Busy: bool = False  # 单元是否繁忙
        self.Op: Operation = None  # 部件执行的指令类型
        self.F_i: FloatRegister = None  # 目的寄存器
        self.F_j: FloatRegister = None  # 源寄存器
        self.F_k: FloatRegister = None  # 源寄存器
        self.Q_j: "Unit" = None  # 如果源寄存器 F_j 不可用, 部件该向哪个功能单元要数据
        self.Q_k: "Unit" = None  # 如果源寄存器 F_k 不可用, 部件该向哪个功能单元要数据
        self.R_j: bool = False  # 源寄存器 F_j 是否可读/需要读
        self.R_k: bool = False  # 源寄存器 F_k 是否可读/需要读


class Unit:
    def __init__(self, name: str, function: UnitFunction) -> None:
        self.name = name
        self.function = function
        self.status = UnitState()
        self.instruction: Instruction = None
        
        self.instructions_buffer: Dict[Instruction, Optional[UnitState]] = {}

    def buffer_instruction(self, instruction: "Instruction"):
        # 如果当前功能单元没有被占用, 直接使用指令
        if self.instruction is None:
            self.instruction = instruction
        else:
            # 否则进入缓冲区
            self.instructions_buffer[instruction] = None
        instruction.unit = self

    def update_status(self, Op: Operation, dest: FloatRegister, reg_j: Union[int, FloatRegister], reg_k: FloatRegister) -> UnitState:
        status = UnitState()
        status.Busy = True
        status.Op = Op
        status.F_i = dest
        
        if type(reg_j) == int:
            status.F_j = None
        else:
            status.F_j = reg_j
            
        status
                    

    def get_info_str(self) -> str:
        info = "    "
        if self.instruction is None or self.status.Busy == False:
            info += " " * 7
        else:
            info += f"{self.instruction.left_latency:>2}/{self.instruction.latency:<2}  "
        info += f"{self.name:<7} | "
        info += f'{"Yes":>4}' if self.status.Busy else f'{"No":>4}'
        if self.status.Busy == False:
            info += " " * 36
        else:
            info += f"  {self.status.Op.value:<6}" if self.status.Op is not None else f" " * 8
            info += f"{self.status.V_j:<6}" if self.status.V_j is not None else f'{" ":<6}'
            info += f"{self.status.V_k:<6}" if self.status.V_k is not None else f'{" ":<6}'
            info += f"{self.status.Q_j:<4}" if self.status.Q_j else f'{" ":<4}'
            info += f"{self.status.Q_k:<4}" if self.status.Q_k else f'{" ":<4}'
            info += f"{self.status.A:<4}" if self.status.A is not None else f'{"":<4}'
            info += f"{self.instruction.rob_item}"
        return info


class InstructionStage(Enum):
    TOBE_ISSUE = "TOBE_ISSUE"
    ISSUE = "ISSUE"
    EXEC = "EXEC"
    MEM = "MEM"
    WRITE = "WRITE"
    COMPLETE = "COMPLETE"


class Instruction:
    def __init__(
        self,
        Op: Operation,
        dest: FloatRegister,
        j: Union[int, FloatRegister],
        k: FloatRegister,
        unit_function: UnitFunction,
        latency: int = 1,
    ) -> None:
        self.Op = Op
        self.dest = dest
        self.j = j
        self.k = k
        self.unit_function = unit_function  # 执行指令需要的功能单元
        self.latency = latency

        self.unit: Unit = None  # 执行当前指令的功能单元
        self.stage: InstructionStage = InstructionStage.TOBE_ISSUE  # 指令执行的阶段
        self.left_latency = self.latency  # 剩余执行时间
        self.stage_clocks: Dict[Enum, Optional[int]] = {
            InstructionStage.ISSUE: None,
            InstructionStage.EXEC: None,
            InstructionStage.MEM: None,
            InstructionStage.WRITE: None,
        }  # 四个阶段进入的时间节点

    def run(self):
        if self.stage == InstructionStage.WRITE:
            return

        # 其实并未真的进入发射阶段, 只是指令流出
        if self.stage == InstructionStage.TOBE_ISSUE:
            self.stage = InstructionStage.ISSUE
            if self.unit.instruction == self:
                self.unit.update_status(self.Op, self.dest, self.j, self.k)
            else:
                self
            self.stage_clocks[InstructionStage.ISSUE] = CLOCK

        elif self.stage == InstructionStage.ISSUE:
            # 如果当前功能单元并不在被当前指令占用, 返回
            if self.unit.instruction != self:
                return
            
            # 如果有需要等待的数据, 直接返回
            if self.unit.status.Q_j or self.unit.status.Q_k:
                return

            self.stage = InstructionStage.EXEC
            self.left_latency -= 1
            if self.left_latency == 0:
                self.stage_clocks[InstructionStage.EXEC] = CLOCK

        elif self.stage == InstructionStage.EXEC:
            ...

        elif self.stage == InstructionStage.MEM:
            ...

    def get_info_str(self) -> str:
        info = ""
        for stage, clock in self.stage_clocks.items():
            info += f"{clock:>6}" if clock is not None else " " * 6
            
        return info

    def __format__(self, __format_spec: str) -> str:
        
        dest_name = self.dest if type(self.dest) == str else self.dest.name
        info = f"{self.Op.name:<5} {dest_name:<4} {self.j if type(self.j) == int else self.j.name:>2} {self.k.name:>2}"
        return format(info, __format_spec)


class SuperScale:
    def __init__(self, multi_issue_number: int, rg: RegisterGroup) -> None:
        self.multi_issue_number = multi_issue_number  # 超标量个数
        self.register_group = rg
        self.instructions: List[Instruction] = []
        self.pc: int = 0
        self.functional_units: List[Unit] = [
            Unit(name="Address Adder", function=UnitFunction.INTEGER),
            Unit(name="Integer ALU", function=UnitFunction.ADD),
            Unit(name="FP ALU", function=UnitFunction.FADD),
        ]
        self.issued_instructions: List[Instruction] = []  # 所有已发射的指令

    def load_instructions(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.pc = 0

    def run(self):
        self.show_status()
        global CLOCK
        CLOCK += 1

        instruction_length = len(self.instructions)
        while True:
            # 当全部指令都已发射并且所有 Unit 都空闲时退出
            if self.pc >= instruction_length:
                busy_unit_number = 0
                for unit in self.functional_units:
                    if unit.status.Busy:
                        busy_unit_number += 1
                if busy_unit_number == 0:
                    break

            # 发射两条新指令
            if self.pc != instruction_length:
                branch_operators = [Operation.BNE]
                for _ in range(self.multi_issue_number):
                    instruction = self.instructions[self.pc]
                    unit = self.get_unit(instruction.unit_function)
                    unit.buffer_instruction(instruction)
                    self.issued_instructions.append(instruction)
                    self.pc += 1
                    # 如果是分支指令则发射一条指令
                    if instruction.Op in branch_operators:
                        break
                    if self.pc >= instruction_length:
                        break
                    # 如果下一条是分支则也停止
                    if self.instructions[self.pc].Op in branch_operators:
                        break
        
            # 所有指令发射后交由指令本身去执行
            # 指令内部维护 issue -> exec -> mem -> write 的执行顺序
            for instruction in self.issued_instructions:
                instruction.run()

            # 所有指令都执行结束之后一起更新 unit 的 Qj Qk 的状态, 避免指令串行更新的干扰
            for unit in self.functional_units:
                ...

            self.show_status()
            CLOCK += 1
            pass
            # exit()

    def get_unit(self, unit_function: UnitFunction) -> Unit:
        """
        检查当前缓冲区是否还有 unit_function 类的功能单元可用

        如有返回对应的 Unit
        没有返回 None
        """
        for unit in self.functional_units:
            if unit.function == unit_function:
                return unit

        raise ValueError("fail to find available unit")

    def show_status(self):
        print("-" * 70)
        print("[instruction status]\n")
        print(f"    Instructions     | Issue  Exec   Mem Write | Comment")
        for instruction in self.instructions:
            print(f"    {instruction:<17}", end="|")
            print(instruction.get_info_str())
        print("\n")


def main():
    rg = RegisterGroup()
    rg.R1.value = 200
    rg.R2.value = 300

    instructions = [
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
        
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
        
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
    ]

    isa = SuperScale(multi_issue_number=2, rg=rg)
    isa.load_instructions(instructions)
    isa.run()


if __name__ == "__main__":
    main()
