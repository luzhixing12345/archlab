from enum import Enum
from typing import List, Optional, Union, Dict

CLOCK = 0


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
    def __init__(self, name: str) -> None:
        self.name = name
        self.ready_to_be_read = True  # 当前寄存器是否可以被读
        self.be_asked_to_read = 0  # 正在读当前寄存器的 unit 的数量 (用于 WAR) 的判断
        self.in_used_unit: Optional["Unit"] = None # 正在使用当前寄存器作为目的寄存器的 unit

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

        self.usage_data: Dict[Instruction, List[int]] = {}

    def update_status(self, Op: Operation, dest: FloatRegister, reg_j: Union[int, FloatRegister], reg_k: FloatRegister):
        self.status.Busy = True
        self.status.Op = Op
        self.status.F_i = dest
        self.status.F_i.in_used_unit = self
        self.status.F_i.ready_to_be_read = False

        if type(reg_j) == int:
            # 立即数
            self.status.F_j = None
            self.status.R_j = True
            self.status.Q_j = None
        else:
            self.status.F_j = reg_j
            self.status.R_j = reg_j.ready_to_be_read
            self.status.Q_j = reg_j.in_used_unit

            if self.status.R_j:
                self.status.F_j.be_asked_to_read += 1

        self.status.F_k = reg_k
        self.status.R_k = reg_k.ready_to_be_read
        self.status.Q_k = reg_k.in_used_unit

        if self.status.R_k:
            self.status.F_k.be_asked_to_read += 1

    def finish_read(self):
        self.status.R_j = False
        self.status.R_k = False
        if self.status.F_j is not None:
            self.status.F_j.be_asked_to_read -= 1
        self.status.F_k.be_asked_to_read -= 1

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
            info += f"  {self.status.Op.value:<4}  " if self.status.Op is not None else f" " * 8
            info += f"{self.status.F_i.name:<4}" if self.status.F_i else f'{" ":<4}'
            info += f"{self.status.F_j.name:<4}" if self.status.F_j else f'{" ":<4}'
            info += f"{self.status.F_k.name:<4}" if self.status.F_k else f'{" ":<4}'
            info += f"{self.status.Q_j.name:<8}" if self.status.Q_j else f'{" ":<8}'
            info += f"{self.status.Q_k.name:<8}" if self.status.Q_k else f'{" ":<8}'
        info += f'{"Yes":<4}' if self.status.R_j else f'{"No":<4}'
        info += f'{"Yes":<4}' if self.status.R_k else f'{"No":<4}'
        return info

    def get_usage_data(self) -> str:
        info = f"{self.name:<9}"

        for i, (instruction, stage_clock) in enumerate(self.usage_data.items()):
            if i != 0:
                info += ' ' * 9
            info += f"{instruction.Op.name} {instruction.dest.name} {instruction.j if type(instruction.j) == int else instruction.j.name} {instruction.k.name}".ljust(16)
            info += f"{stage_clock[0]:>5}   {stage_clock[-1]:>3}"
            info += f"     {3 + instruction.latency}/{stage_clock[-1]-stage_clock[0] + 1}\n"
        return info


class InstructionStage(Enum):
    TOBE_ISSUE = "TOBE_ISSUE"
    ISSUE = "ISSUE"
    READ = "READ"
    EXEC = "EXEC"
    WRITE = "WRITE"
    COMPLETE = "COMPLETE"


class Instruction:
    def __init__(
        self,
        Op: Operation,
        dest: FloatRegister,
        j: Union[int, FloatRegister],
        k: FloatRegister,
        latency: int,
        unit_function: UnitFunction,
    ) -> None:
        self.Op = Op
        self.dest = dest
        self.j = j
        self.k = k
        self.latency = latency
        self.unit_function = unit_function  # 执行指令需要的功能单元

        self.unit: Unit = None  # 执行当前指令的功能单元
        self.stage: InstructionStage = InstructionStage.TOBE_ISSUE  # 指令执行的阶段
        self.left_latency = self.latency # 剩余执行时间
        self.stage_clocks = []  # 四个阶段进入的时间节点

    def run(self):
        """ """
        if self.stage == InstructionStage.COMPLETE:
            return

        if self.stage == InstructionStage.TOBE_ISSUE:
            self.stage = InstructionStage.ISSUE
            self.unit.update_status(self.Op, self.dest, self.j, self.k)
            self.stage_clocks.append(CLOCK)

        elif self.stage == InstructionStage.ISSUE:
            # 当两个源寄存器都可读的时候继续
            if self.unit.status.R_j and self.unit.status.R_k:
                self.stage = InstructionStage.READ
                self.stage_clocks.append(CLOCK)

        elif self.stage == InstructionStage.READ:
            self.stage = InstructionStage.EXEC
            self.unit.finish_read()
            self.left_latency -= 1
            if self.left_latency == 0:
                self.stage_clocks.append(CLOCK)

        elif self.stage == InstructionStage.EXEC:
            if self.left_latency > 0:
                self.left_latency -= 1
                if self.left_latency == 0:
                    self.stage_clocks.append(CLOCK)
            else:
                if self.unit.status.F_i.be_asked_to_read != 0:
                    # WAR hazard
                    return
                self.stage = InstructionStage.WRITE
                self.unit.status.Busy = False
                self.unit.status.F_i.in_used_unit = None
                self.unit.status.F_i.ready_to_be_read = True
                self.stage = InstructionStage.COMPLETE
                self.stage_clocks.append(CLOCK)

                # 添加统计数据
                self.unit.usage_data[self] = self.stage_clocks

    def get_info_str(self) -> str:
        info = ""
        for stage_clock in self.stage_clocks:
            info += f"{stage_clock:>6}"

        return info


class ScoreBoard:
    def __init__(self, rg: RegisterGroup) -> None:
        self.instructions: List[Instruction] = []
        self.issued_instructions: List[Instruction] = []
        self.pc: int = 0
        self.functional_units: List[Unit] = [
            Unit(name="Integer", function=UnitFunction.INTEGER),
            Unit(name="Mult1", function=UnitFunction.MULT),
            Unit(name="Mult2", function=UnitFunction.MULT),
            Unit(name="Add", function=UnitFunction.ADD),
            Unit(name="Divide", function=UnitFunction.DIVIDE),
        ]
        self.register_group = rg

    def load_instructions(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.pc = 0

    def run(self):
        self.show_status()
        global CLOCK
        CLOCK += 1

        instruction_length = len(self.instructions)
        while True:
            # 当全部指令都已发射并且所有功能单元都空闲时退出
            if self.pc == instruction_length:
                busy_unit_number = 0
                for unit in self.functional_units:
                    if unit.status.Busy:
                        busy_unit_number += 1
                if busy_unit_number == 0:
                    break

            # 尝试发射一条新指令
            # 1. 如果有指令
            # 2. 并且有可用的功能单元
            # 3. 且指令要写的目的寄存器没有别的指令将要写
            # 则发射下一条指令
            if self.pc != instruction_length:
                unit = self.has_available_unit(self.instructions[self.pc].unit_function)
                if unit is not None and not self.has_write_conflict(self.instructions[self.pc].dest):
                    self.instructions[self.pc].unit = unit
                    unit.instruction = self.instructions[self.pc]
                    self.issued_instructions.append(self.instructions[self.pc])
                    self.pc += 1

            # 所有指令发射后交由指令本身去执行
            # 指令内部维护 issue -> read -> exec -> write 的执行顺序
            for issued_instruction in self.issued_instructions:
                issued_instruction.run()

            # 所有指令都执行结束之后一起更新 unit 的 Rj Rk Qj Qk 的状态, 避免指令串行更新的干扰
            for unit in self.functional_units:
                if unit.status.R_j == False and unit.status.Q_j and unit.status.Q_j.status.Busy == False:
                    unit.status.R_j = True
                    unit.status.Q_j = None
                if unit.status.R_k == False and unit.status.Q_k and unit.status.Q_k.status.Busy == False:
                    unit.status.R_k = True
                    unit.status.Q_k = None

            self.show_status()
            CLOCK += 1
            pass
            # exit()

        self.show_usage_data()

    def has_available_unit(self, unit_function: UnitFunction) -> Optional[Unit]:
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

    def show_status(self):
        print("-" * 70)
        print("[#instruction status#]\n")
        print(f"    Op   dest j   k  | Issue  Read  Exec  Write")
        for instruction in self.instructions:
            print(f"    {instruction.Op.value:<4} {instruction.dest:<4} {instruction.j}  {instruction.k}", end=" |")
            print(instruction.get_info_str())
        print("\n")
        print("[#functional unit status#]\n")
        print("    Time   Name    | Busy  Op    Fi  Fj  Fk  Qj      Qk      Rj  Rk")
        for unit in self.functional_units:
            print(unit.get_info_str())
        print("\n")
        print("[#register result status#]\n")
        print(self.register_group)
        print("\n")

    def show_usage_data(self):
        print("Unit     Instruction     start   end     theoretical/running")
        for unit in self.functional_units:
            print(unit.get_usage_data())


def main():
    rg = RegisterGroup()

    instructions = [
        Instruction(Op=Operation.LOAD, dest=rg.F6, j=34, k=rg.R2, latency=1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.LOAD, dest=rg.F2, j=45, k=rg.R3, latency=1, unit_function=UnitFunction.INTEGER),
        Instruction(Op=Operation.MUL, dest=rg.F0, j=rg.F2, k=rg.F4, latency=10, unit_function=UnitFunction.MULT),
        Instruction(Op=Operation.SUB, dest=rg.F8, j=rg.F6, k=rg.F2, latency=2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.DIV, dest=rg.F10, j=rg.F0, k=rg.F6, latency=40, unit_function=UnitFunction.DIVIDE),
        Instruction(Op=Operation.ADD, dest=rg.F6, j=rg.F8, k=rg.F2, latency=2, unit_function=UnitFunction.ADD),
    ]

    scoreboard = ScoreBoard(rg)
    scoreboard.load_instructions(instructions)
    scoreboard.run()


if __name__ == "__main__":
    main()
