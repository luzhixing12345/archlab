from enum import Enum
from typing import List, Optional, Union

CLOCK = 0


class Operation(Enum):
    LOAD = "Load"
    STORE = "Store"
    SUB = "Sub"
    ADD = "Add"
    BNE = 'Bne'


class UnitFunction(Enum):
    LOAD = "Load"
    MULT = "Mult"
    ADD = "Add"


class FloatRegister:
    def __init__(self, name: str) -> None:
        self.name = name
        self.value = 0
        self.in_used_unit: Optional["Unit"] = None  # 正在使用当前寄存器作为目的寄存器的 unit
        self.in_rob_item: Optional["ReorderBufferItem"] = None

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

    def __repr__(self) -> str:
        info = " " * 13

        for name, _ in self.register_map.items():
            info += f"{name:<3} "
        info += "\n"
        info += f"   Cycle {CLOCK:<2}  "
        for _, reg in self.register_map.items():
            if reg.in_rob_item:
                info += f'{"#" + str(reg.in_rob_item.entry):<4}'
            else:
                info += " " * 4

        return info


class UnitState:
    def __init__(self) -> None:
        self.Busy: bool = False  # 单元是否繁忙
        self.Op: Operation = None  # 部件执行的指令类型
        self.V_j: Optional[int] = None  # 源寄存器 j 的值
        self.V_k: Optional[int] = None  # 源寄存器 k 的值
        self.Q_j: "ReorderBufferItem" = None  # 如果源寄存器 j 的值暂不可读, 部件该向哪个功能单元要数据
        self.Q_k: "ReorderBufferItem" = None  # 如果源寄存器 k 的值暂不可读, 部件该向哪个功能单元要数据
        self.A: Optional[int] = None  # 地址, 对于 Load/Store Unit 有效
        self.dest: "ReorderBufferItem" = None


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

        assert dest.in_used_unit is None  # 写回寄存器不应该存在冲突
        dest.in_used_unit = self
        dest.in_rob_item = self.instruction.rob_item

        if type(reg_j) == int:
            self.status.A = reg_j
            if reg_k.in_rob_item is None:
                self.status.V_k = reg_k.value
            else:
                self.status.Q_k = reg_k.in_rob_item
        else:
            if reg_j.in_rob_item is None:
                self.status.V_j = reg_j.value
            else:
                self.status.Q_j = reg_j.in_rob_item

            if reg_k.in_rob_item is None:
                self.status.V_k = reg_k.value
            else:
                self.status.Q_k = reg_k.in_rob_item

    def exec(self):
        if self.status.Op == Operation.LOAD:
            # 正常应该从 Memory 取数据
            # 这里偷个懒, 直接认为 Memory[addr] = addr
            self.status.A += self.status.V_k
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
        # "    Time   Name    | Busy  Op    Vj    Vk    Qj  Qk  A   Dest"
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
    WRITE = "WRITE"
    COMMIT = "COMMIT"


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
        self.rob_item: "ReorderBufferItem" = None
        self.left_latency = self.latency  # 剩余执行时间
        self.stage_clocks = []  # 四个阶段进入的时间节点
        self.return_value = None

    def run(self):
        if self.stage == InstructionStage.COMMIT:
            return

        # 如果尚未发射进入发射阶段
        if self.stage == InstructionStage.TOBE_ISSUE:
            self.stage = InstructionStage.ISSUE
            self.unit.update_status(self.Op, self.dest, self.j, self.k)
            self.rob_item.Busy = True
            self.stage_clocks.append(CLOCK)

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

        elif self.stage == InstructionStage.EXEC:
            if self.return_value is not None:
                self.stage = InstructionStage.WRITE
                self.rob_item.value = self.return_value
                self.unit.status.Busy = False
                self.dest.in_used_unit = None
                self.stage_clocks.append(CLOCK)
            else:
                self.left_latency -= 1
                if self.left_latency == 0:
                    self.return_value = self.unit.exec()
                    self.stage_clocks.append(CLOCK)

        elif self.stage == InstructionStage.WRITE:
            # 只有是 head 的时候才可以 commit
            if self.rob_item.parent_rob.head + 1 == self.rob_item.entry:
                # 更新 head 指针, 避免指令顺序影响
                self.rob_item.parent_rob.is_head_move = True
                self.stage = InstructionStage.COMMIT
                self.dest.value = self.rob_item.value
                self.dest.in_rob_item = None
                self.rob_item.Busy = False
                self.stage_clocks.append(CLOCK)

    def get_info_str(self) -> str:
        info = ""
        for stage_clock in self.stage_clocks:
            info += f"{stage_clock:>6}"

        return info

    def __format__(self, __format_spec: str) -> str:
        info = f"{self.Op.name} {self.dest.name} {self.j if type(self.j) == int else self.j.name} {self.k.name}"
        return format(info, __format_spec)


class ReorderBufferItem:
    def __init__(self, entry: int, parent_rob: "ReorderBuffer") -> None:
        self.entry = entry

        self.Busy: bool = False
        self.value = None

        self.instruction: Instruction = None
        self.parent_rob: ReorderBuffer = parent_rob

    def __format__(self, __format_spec: str) -> str:
        return format(f"#{str(self.entry)}", __format_spec)


class ReorderBuffer:
    def __init__(self, buffer_size: int) -> None:
        self.buffer_size = buffer_size
        self.head = 0
        self.tail = -1
        self.buffer: List[ReorderBufferItem] = []
        for i in range(1, buffer_size + 1):
            self.buffer.append(ReorderBufferItem(i, self))

        self.is_head_move = False # head 指针是否移动
        self.issued_instructions: List[Instruction] = []

    def insert(self, instruction: Instruction):
        self.tail = (self.tail + 1) % self.buffer_size
        instruction.rob_item = self.buffer[self.tail]
        self.buffer[self.tail].instruction = instruction
        self.issued_instructions.append(instruction)

    def run(self):
        for issued_instruction in self.issued_instructions:
            issued_instruction.run()

    def is_available(self) -> bool:
        """
        ROB 有空闲
        """
        return self.tail == -1 or (self.tail + 1) % self.buffer_size != self.head

    def get_info_str(self) -> str:
        # "Entry Busy Instruction         Stat    Dest  value"
        info = ""
        for i, buffer_item in enumerate(self.buffer):
            if i == self.head and self.head == self.tail:
                info += " H/T -> "
            elif i == self.head:
                info += "head -> "
            elif i == self.tail:
                info += "tail -> "
            else:
                info += "        "
            info += f"{buffer_item.entry:>5} "
            info += f'{"Yes":>4} ' if buffer_item.Busy else f'{"No":>4} '
            if buffer_item.instruction is None:
                info += " " * 24
            else:
                info += f"{buffer_item.instruction:<20}"
                info += f"{buffer_item.instruction.stage.value:<8}"
                info += f"{buffer_item.instruction.dest.name:<6}"
            if buffer_item.value is not None:
                info += str(buffer_item.value)
            info += "\n"

        return info


class SuperScale:
    def __init__(self, rg: RegisterGroup) -> None:
        self.register_group = rg
        self.instructions: List[Instruction] = []
        self.pc: int = 0
        self.functional_buffers: List[Buffer] = [
            Buffer(function=UnitFunction.LOAD, buffer_size=3),
            Buffer(function=UnitFunction.ADD, buffer_size=2),
            Buffer(function=UnitFunction.MULT, buffer_size=2),
        ]
        self.reorder_buffer = ReorderBuffer(buffer_size=6)

    def load_instructions(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.pc = 0

    def run(self):
        self.show_status()
        global CLOCK
        CLOCK += 1

        instruction_length = len(self.instructions)
        while True:
            # 当全部指令都已发射并且所有 ROB 都空闲时退出
            if self.pc == instruction_length:
                busy_rob_number = 0
                for buffer in self.reorder_buffer.buffer:
                    busy_rob_number += buffer.Busy
                if busy_rob_number == 0:
                    break

            # 尝试发射一条新指令
            # 1. 如果有指令
            # 2. 对应的功能单元还有 buffer
            # 3. ROB 还有空位
            # 则发射下一条指令
            if self.pc != instruction_length:
                unit = self.has_available_buffer(self.instructions[self.pc].unit_function)
                if unit is not None and self.reorder_buffer.is_available():
                    # 绑定 instruction <-> unit
                    self.instructions[self.pc].unit = unit
                    unit.instruction = self.instructions[self.pc]
                    # 绑定 instruction <-> rob
                    self.reorder_buffer.insert(self.instructions[self.pc])
                    self.pc += 1

            # 所有指令发射后交由指令本身去执行
            # 指令内部维护 issue -> exec -> write -> commit 的执行顺序
            self.reorder_buffer.run()

            # 所有指令都执行结束之后一起更新 unit 的 Qj Qk 的状态, 避免指令串行更新的干扰
            for buffer in self.functional_buffers:
                for unit in buffer.units:
                    if unit.status.Q_j and unit.status.Q_j.instruction.stage == InstructionStage.WRITE:
                        unit.status.V_j = unit.status.Q_j.instruction.dest.value
                        unit.status.Q_j = None

                    if unit.status.Q_k and unit.status.Q_k.instruction.stage == InstructionStage.WRITE:
                        unit.status.V_k = unit.status.Q_k.instruction.dest.value
                        unit.status.Q_k = None

            # 只会更新一次
            if self.reorder_buffer.is_head_move:
                self.reorder_buffer.head = (self.reorder_buffer.head + 1) % self.reorder_buffer.buffer_size
                self.reorder_buffer.is_head_move = False

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
        print(f"    Op     dest j   k   | Issue  Exec  Write  Commit")
        for instruction in self.instructions:
            print(f"    {instruction.Op.value:<6} {instruction.dest:<4} {instruction.j:<4}{instruction.k:<3}", end=" |")
            print(instruction.get_info_str())
        print("\n")
        print("[reorder buffer]\n")
        print("        Entry Busy Instruction         Stat    Dest  value")
        print(self.reorder_buffer.get_info_str())
        print("[reservation station]\n")
        print("    Time   Name    | Busy  Op    Vj    Vk    Qj  Qk  A   Dest")
        for buffer in self.functional_buffers:
            print(buffer.get_info_str())
        print("\n")
        print("[register result status]\n")
        print(self.register_group)
        print("\n")


def main():
    rg = RegisterGroup()
    rg.R1.value = 200
    rg.R2.value = 300

    instructions = [
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, latency=1, unit_function=UnitFunction.LOAD),
        Instruction(Op=Operation.ADD, dest=rg.F4, j=rg.F0, k=rg.F2, latency=2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, latency=2, unit_function=UnitFunction.LOAD),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, latency=1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest=rg.R1, j=rg.R1, k=rg.R1, latency=1, unit_function=UnitFunction.ADD),
    ]

    isa = SuperScale(rg)
    isa.load_instructions(instructions)
    isa.run()


if __name__ == "__main__":
    main()
