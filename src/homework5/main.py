from enum import Enum
from typing import List, Optional, Union

CLOCK = 0


class Operation(Enum):
    LOAD = "Load"
    STORE = "Store"
    MUL = "Mul"
    SUB = "Sub"
    DIV = "Div"
    ADD = "Add"


class UnitFunction(Enum):
    LOAD = "Load"
    STORE = "Store"
    MULT = "Mult"
    ADD = "Add"


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
        self.V_j: Optional[int] = None # 源寄存器 j 的值
        self.V_k: Optional[int] = None # 源寄存器 k 的值
        self.Q_j: "Unit" = None  # 如果源寄存器 j 的值暂不可读, 部件该向哪个功能单元要数据
        self.Q_k: "Unit" = None  # 如果源寄存器 k 的值暂不可读, 部件该向哪个功能单元要数据
        self.A: Optional[int] = None  # 地址, 对于 Load/Store Unit 有效


class Buffer:
    def __init__(self, function: UnitFunction, buffer_size: int) -> None:
        self.units: List["Unit"] = []
        self.function = function
        for i in range(1, buffer_size + 1):
            unit = Unit(name=f"{function.value}{i}", function=function)
            unit.buffer = self
            self.units.append(unit)

    def get_busy_unit_number(self):
        busy_unit_number = 0
        for unit in self.units:
            if unit.status.Busy:
                busy_unit_number += 1
        return busy_unit_number

    def check_exec_instruction(self):
        """
        真正可以用于计算的功能部件只有一个, 因此同一时刻在一个 buffer 内部
        只能有一个指令进入执行阶段, 其余等候
        """
        for unit in self.units:
            if unit.instruction is not None and unit.instruction.stage == InstructionStage.EXEC:
                return True
        return False

    def get_info_str(self):
        info = ""
        for unit in self.units:
            info += unit.get_info_str() + "\n"
        return info[:-1]


class Unit:
    def __init__(self, name: str, function: UnitFunction) -> None:
        self.name = name
        self.function = function
        self.status = UnitState()
        self.instruction: Instruction = None
        self.buffer: Buffer = None

    def update_status(self, Op: Operation, dest: FloatRegister, reg_j: Union[int, FloatRegister], reg_k: FloatRegister):
        self.status.Busy = True
        self.status.Op = Op

        if Op in (Operation.LOAD, Operation.STORE):
            # 对于 Load/Store 指令来说需要先计算目的地址
            if reg_k.in_used_unit is not None:
                self.status.Q_k = reg_k.in_used_unit
            else:
                # 对于 Load 指令
                #   j       -> A
                #   reg_k   -> Vk

                # 对于 Store 指令, dest 寄存器的值要在一开始读出来, 但是没有额外的空间了, 所以放在 Vj
                #   dest    -> Vj
                #   j       -> A
                #   reg_k   -> Vk
                if Op == Operation.STORE:
                    if dest.in_used_unit is not None:
                        self.status.Q_j = dest.in_used_unit
                    else:
                        self.status.V_j = dest.value
                else:
                    assert dest.in_used_unit is None  # 写回寄存器不应该存在冲突
                    dest.in_used_unit = self
                self.status.A = reg_j
                self.status.V_k = reg_k.value
                self.instruction.stage = InstructionStage.CALC
            return

        assert dest.in_used_unit is None  # 写回寄存器不应该存在冲突
        dest.in_used_unit = self

        if reg_j.in_used_unit is None:
            self.status.V_j = reg_j.value
        else:
            self.status.Q_j = reg_j.in_used_unit

        if reg_k.in_used_unit is None:
            self.status.V_k = reg_k.value
        else:
            self.status.Q_k = reg_k.in_used_unit

    def exec(self):
        if self.status.Op == Operation.LOAD:
            # 正常应该从 Memory 取数据
            # 这里偷个懒, 直接认为 Memory[addr] = addr
            return self.status.A
        elif self.status.Op == Operation.ADD:
            return self.status.V_j + self.status.V_k
        elif self.status.Op == Operation.MUL:
            return self.status.V_j * self.status.V_k
        elif self.status.Op == Operation.DIV:
            return self.status.V_j / self.status.V_k
        elif self.status.Op == Operation.SUB:
            return self.status.V_j - self.status.V_k
        # STORE 没有返回值

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
            info += f"{self.status.Q_j.name:<8}" if self.status.Q_j else f'{" ":<8}'
            info += f"{self.status.Q_k.name:<8}" if self.status.Q_k else f'{" ":<8}'
            info += f"{self.status.A}" if self.status.A is not None else ""
        return info


class InstructionStage(Enum):
    TOBE_ISSUE = "TOBE_ISSUE"
    ISSUE = "ISSUE"
    CALC = "CALC"
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
        self.left_latency = self.latency  # 剩余执行时间
        self.stage_clocks = []  # 四个阶段进入的时间节点
        self.return_value = None

    def run(self):
        if self.stage == InstructionStage.COMPLETE:
            return

        # 如果尚未发射进入发射阶段
        if self.stage == InstructionStage.TOBE_ISSUE:
            self.stage = InstructionStage.ISSUE

            # 对于带立即数的指令(load/store), update_status 会进入 InstructionStage.CALC 阶段
            self.unit.update_status(self.Op, self.dest, self.j, self.k)
            self.stage_clocks.append(CLOCK)

        # load/store 需要两个周期完成发射
        # 因为在 ISSUE 阶段还需要额外一个周期来计算 Vk + imm 的结果
        elif self.stage == InstructionStage.CALC:
            self.unit.status.A = self.unit.status.A + self.unit.status.V_k
            self.stage = InstructionStage.ISSUE
            # 计算完成之后就不需要 Vk 了, 为了输出好看一些
            self.unit.status.V_k = None

        elif self.stage == InstructionStage.ISSUE:
            # 如果有需要等待的数据, 直接返回
            if self.unit.status.Q_j or self.unit.status.Q_k:
                return

            # 进入执行阶段前需要判断当前 buffer 是否有其他正在执行的单元
            # 因为只有一个功能部件, 如果有其他指令正在使用则当前指令需要等待
            if self.unit.buffer.check_exec_instruction():
                return

            self.stage = InstructionStage.EXEC
            self.left_latency -= 1
            if self.left_latency == 0:
                self.return_value = self.unit.exec()
                self.stage_clocks.append(CLOCK)
                self.stage = InstructionStage.WRITE

        elif self.stage == InstructionStage.EXEC:
            self.left_latency -= 1
            if self.left_latency == 0:
                self.return_value = self.unit.exec()
                self.stage_clocks.append(CLOCK)
                self.stage = InstructionStage.WRITE

        elif self.stage == InstructionStage.WRITE:
            if self.return_value is not None:
                self.dest.value = self.return_value
            self.stage = InstructionStage.COMPLETE
            self.unit.status.Busy = False
            if self.dest:
                self.dest.in_used_unit = None
            self.stage_clocks.append(CLOCK)

    def get_info_str(self) -> str:
        info = ""
        for stage_clock in self.stage_clocks:
            info += f"{stage_clock:>6}"

        return info


class Tomasulo:
    def __init__(self, rg: RegisterGroup) -> None:
        self.instructions: List[Instruction] = []
        self.issued_instructions: List[Instruction] = []
        self.pc: int = 0
        self.functional_buffers: List[Buffer] = [
            Buffer(function=UnitFunction.LOAD, buffer_size=3),
            Buffer(function=UnitFunction.STORE, buffer_size=3),
            Buffer(function=UnitFunction.ADD, buffer_size=2),
            Buffer(function=UnitFunction.MULT, buffer_size=2),
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
            # 当全部指令都已发射并且所有 buffer 的所有功能单元都空闲时退出
            if self.pc == instruction_length:
                busy_unit_number = 0
                for buffer in self.functional_buffers:
                    busy_unit_number += buffer.get_busy_unit_number()
                if busy_unit_number == 0:
                    break

            # 尝试发射一条新指令
            # 1. 如果有指令
            # 2. 对应的功能单元还有 buffer
            # 则发射下一条指令
            if self.pc != instruction_length:
                unit = self.has_available_buffer(self.instructions[self.pc].unit_function)
                if unit is not None:
                    self.instructions[self.pc].unit = unit
                    unit.instruction = self.instructions[self.pc]
                    self.issued_instructions.append(self.instructions[self.pc])
                    self.pc += 1

            # 所有指令发射后交由指令本身去执行
            # 指令内部维护 issue + read -> exec -> write 的执行顺序
            for issued_instruction in self.issued_instructions:
                issued_instruction.run()

            # 所有指令都执行结束之后一起更新 unit 的 Qj Qk 的状态, 避免指令串行更新的干扰
            for buffer in self.functional_buffers:
                for unit in buffer.units:
                    if unit.status.Q_j and unit.status.Q_j.status.Busy == False:
                        unit.status.V_j = unit.status.Q_j.instruction.dest.value
                        unit.status.Q_j = None

                    if unit.status.Q_k and unit.status.Q_k.status.Busy == False:
                        unit.status.V_k = unit.status.Q_k.instruction.dest.value
                        unit.status.Q_k = None

            self.show_status()
            CLOCK += 1
            pass
            # exit()

    def has_available_buffer(self, unit_function: UnitFunction) -> Optional[Unit]:
        """
        检查当前缓冲区是否还有 unit_function 类的功能单元可用

        如有返回对应的 Unit
        没有返回 None
        """
        for buffer in self.functional_buffers:
            if buffer.function == unit_function:
                for unit in buffer.units:
                    if unit.status.Busy == False:
                        return unit

        return None

    def show_status(self):
        print("-" * 70)
        print("[instruction status]\n")
        print(f"    Op     dest j   k   | Issue  Exec  Write")
        for instruction in self.instructions:
            print(f"    {instruction.Op.value:<6} {instruction.dest:<4} {instruction.j:<4}{instruction.k:<3}", end=" |")
            print(instruction.get_info_str())
        print("\n")
        print("[functional unit status]\n")
        print("    Time   Name    | Busy  Op    Vj    Vk    Qj      Qk      A")
        for buffer in self.functional_buffers:
            print(buffer.get_info_str())
        print("\n")
        print("[register result status]\n")
        print(self.register_group)
        print("\n")


def main():
    rg = RegisterGroup()
    rg.R2.value = 200
    rg.R3.value = 300

    instructions = [
        Instruction(Op=Operation.LOAD, dest=rg.F6, j=34, k=rg.R2, latency=1, unit_function=UnitFunction.LOAD),
        Instruction(Op=Operation.LOAD, dest=rg.F2, j=45, k=rg.R3, latency=1, unit_function=UnitFunction.LOAD),
        Instruction(Op=Operation.MUL, dest=rg.F0, j=rg.F2, k=rg.F4, latency=10, unit_function=UnitFunction.MULT),
        Instruction(Op=Operation.SUB, dest=rg.F8, j=rg.F6, k=rg.F2, latency=2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.DIV, dest=rg.F10, j=rg.F0, k=rg.F6, latency=40, unit_function=UnitFunction.MULT),
        Instruction(Op=Operation.ADD, dest=rg.F6, j=rg.F8, k=rg.F2, latency=2, unit_function=UnitFunction.ADD),
    ]

    isa = Tomasulo(rg)
    isa.load_instructions(instructions)
    isa.run()


if __name__ == "__main__":
    main()
