from enum import Enum
from typing import TypedDict, List, Optional
import logging

CLOCK = 1
LOG_DEBUG_INFO = False


class Operation(Enum):
    LOAD = "Load"
    MUL = "Mul"
    SUB = "Sub"
    DIV = "Div"
    ADD = "Add"


class UnitFunction(Enum):
    INTEGER = "Integer"
    MULT = "Mult"
    ADD = "Add"
    DIVIDE = "Divide"


class FloatRegister:
    ...


class FloatRegGroup:
    F0 = FloatRegister()
    F2 = FloatRegister()
    F4 = FloatRegister()
    F6 = FloatRegister()
    F8 = FloatRegister()
    F10 = FloatRegister()


class UnitState:
    def __init__(self) -> None:
        self.Busy: bool  # 单元是否繁忙
        self.Op: Operation  # 部件执行的指令类型
        self.F_i: int  # 目的寄存器
        self.F_j: int  # 源寄存器
        self.F_k: int  # 源寄存器
        self.Q_j: int  # 如果源寄存器 F_j 没准备好部件该向哪里要数据
        self.Q_k: int  # 如果源寄存器 F_k 没准备好部件该向哪里要数据
        self.R_j: bool  # 源寄存器 F_j 是否准备好
        self.R_k: bool  # 源寄存器 F_k 是否准备好


class Unit:
    def __init__(self, name: str, function: UnitFunction) -> None:
        self.name = name
        self.function = function
        self.status = UnitState()


class InstructionStage(Enum):
    TOBE_ISSUE = "TOBE_ISSUE"
    ISSUE = "ISSUE"
    READ = "READ"
    EXEC = "EXEC"
    WRITE = "WRITE"
    COMPLETE = "COMPLETE"


class Instruction:
    def __init__(self, Op: Operation, dest: str, j: str, k: str, latency: int, unit_function: UnitFunction) -> None:
        self.Op = Op
        self.dest = dest
        self.j = j
        self.k = k
        self.latency = latency
        self.unit_function = unit_function  # 执行指令需要的功能单元

        self.functional_units: List[Unit] = None  # ScoreBoard 中所有的功能单元
        self.unit: Unit = None  # 执行当前指令的功能单元
        self.stage: InstructionStage = InstructionStage.TOBE_ISSUE  # 指令执行的阶段

    def run(self):
        """ """
        if self.stage:
            return

        assert self.functional_units is not None
        assert self.unit is not None

        if self.stage == InstructionStage.TOBE_ISSUE:
            self.stage = InstructionStage.ISSUE
            self.unit.status.Busy = True
            self.unit.status.Op = self.Op
            self.unit.status.F_i = self.dest
            self.unit.status.F_j = self.j
            self.unit.status.F_k = self.k


class RegisterStatus:
    ...


class ScoreBoard:
    def __init__(self) -> None:
        self.instructions: List[Instruction] = []
        self.issued_instructions: List[Instruction] = []
        self.pc: int = 0
        self.functional_units: List[Unit] = [
            Unit(name="Integer", function=UnitFunction.INTEGER),
            Unit(name="Mult1", function=UnitFunction.MULT),
            Unit(name="Mult2", function=UnitFunction.MULT),
            Unit(name="Add", function=UnitFunction.ADD),
            Unit(name="Divide", function=UnitFunction.ADD),
        ]
        self.register_status = RegisterStatus(self.functional_units)

    def load_instructions(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.pc = 0

    def run(self):
        instruction_length = len(self.instructions)
        while True:
            # 全部指令都已发射 并且 都已执行结束, 退出
            if self.pc == instruction_length and len(self.issued_instructions) == 0:
                break

            # 尝试发射一条新指令
            # 1. 如果有指令
            # 2. 并且有可用的功能单元
            # 3. 且指令要写的目标寄存器没有别的指令将要写
            # 则发射下一条指令
            if self.pc != instruction_length:
                unit = self.has_available_unit(self.instructions[self.pc].unit_function)
                if unit is not None and not self.has_write_conflict(self.instructions[self.pc].dest):
                    self.instructions[self.pc].functional_units = self.functional_units
                    self.instructions[self.pc].unit = unit
                    self.issued_instructions.append(self.instructions[self.pc])
                    self.pc += 1

            # 所有指令发射后交由指令本身去执行
            # 指令内部维护 issue -> read -> exec -> write 的执行顺序
            for issued_instruction in self.issued_instructions:
                issued_instruction.run()

            global CLOCK
            CLOCK += 1

    def has_available_unit(self, unit_function: UnitFunction) -> Optional(Unit):
        """
        检查当前 ScoreBoard 是否有 unit_function 类的功能单元可用

        如有返回对应的 Unit
        没有返回 None
        """
        for unit in self.functional_units:
            if unit.function == unit_function and unit.status.Busy == False:
                return unit

        return None

    def has_write_conflict(self, dest_reg: int) -> bool:
        """ """
        for unit in self.functional_units:
            if unit.status.F_i == dest_reg:
                return True
        return False


def main():
    frg = FloatRegGroup()

    instructions = [
        Instruction(Op=Operation.LOAD, dest=frg.F6, j=34, k="R2", latency=0, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.LOAD, dest=frg.F2, j=45, k="R3", latency=0, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.MUL, dest=frg.F8, j=frg.F2, k=frg.F4, latency=10, unit_function=UnitFunction.MULT),
        Instruction(Op=Operation.SUB, dest=frg.F8, j=frg.F6, k=frg.F2, latency=2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.DIV, dest=frg.F10, j=frg.F0, k=frg.F6, latency=40, unit_function=UnitFunction.DIVIDE),
        Instruction(Op=Operation.ADD, dest=frg.F6, j=frg.F8, k=frg.F2, latency=2, unit_function=UnitFunction.ADD),
    ]

    scoreboard = ScoreBoard()
    scoreboard.load_instructions(instructions)
    global LOG_DEBUG_INFO
    LOG_DEBUG_INFO = True
    scoreboard.run()


if __name__ == "__main__":
    main()
