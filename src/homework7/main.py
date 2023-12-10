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
        self.to_be_write: bool = False

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
            "R1": self.R1,
            "R2": self.R2,
        }

    def __repr__(self) -> str:
        info = "    "
        for name in self.register_map:
            info += f"{name:<4}"
        info += "\n    "
        for _, reg in self.register_map.items():
            info += f'{"Yes" if reg.to_be_write else "No":<4}'
        return info


class UnitState:
    def __init__(self) -> None:
        self.Op: Operation = None  # 部件执行的指令类型
        self.Q_j: bool = False
        self.Q_k: bool = False
        
        self.write_mem: bool = True


class Unit:
    def __init__(self, name: str, function: UnitFunction, CDB: "CDB") -> None:
        self.name = name
        self.function = function
        self.CDB = CDB
        self.instruction: Instruction = None
        self.status: UnitState = None
        self.in_use = False


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
        self.status: UnitState = UnitState()

    def run(self):
        if self.stage == InstructionStage.COMPLETE:
            return

        # 其实并未真的进入发射阶段, 只是指令流出
        if self.stage == InstructionStage.TOBE_ISSUE:
            self.stage = InstructionStage.ISSUE
            self.update_status(self.Op, self.dest, self.j, self.k)
            if self.unit.in_use == False:
                self.unit.in_use = True
                self.unit.instruction = self
                self.unit.status = self.status
            self.stage_clocks[InstructionStage.ISSUE] = CLOCK

        elif self.stage == InstructionStage.ISSUE:
            # 如果当前功能单元并不在被当前指令占用, 返回
            if self.unit.instruction != self:
                if self.unit.in_use == False:
                    self.unit.in_use = True
                    self.unit.instruction = self
                    self.unit.status = self.status
                else:
                    return
            # 如果有需要等待的数据, 直接返回
            if self.unit.status.Q_j or self.unit.status.Q_k:
                return

            self.stage = InstructionStage.EXEC
            self.stage_clocks[InstructionStage.EXEC] = CLOCK
            self.left_latency -= 1

        elif self.stage == InstructionStage.EXEC:
            if self.left_latency == 0:
                if self.Op in (Operation.LOAD, Operation.STORE):
                    if self.Op == Operation.STORE and not self.unit.status.write_mem:
                        return
                    self.stage = InstructionStage.MEM
                    self.stage_clocks[InstructionStage.MEM] = CLOCK
                elif self.Op == Operation.BNE:
                    self.stage = InstructionStage.COMPLETE
                else:
                    if self.unit.CDB.available:
                        self.unit.CDB.send_data()
                        self.stage = InstructionStage.WRITE
                        self.stage_clocks[InstructionStage.WRITE] = CLOCK
            else:
                self.left_latency -= 1

        elif self.stage == InstructionStage.MEM:
            if self.Op == Operation.STORE:
                self.stage = InstructionStage.WRITE
            else:
                if self.unit.CDB.available:
                    self.unit.CDB.send_data()
                    self.stage = InstructionStage.WRITE
                    self.stage_clocks[InstructionStage.WRITE] = CLOCK

        else:
            # WRITE
            self.stage = InstructionStage.COMPLETE

    def update_status(self, Op: Operation, dest: FloatRegister, reg_j: Union[int, FloatRegister], reg_k: FloatRegister):
        self.status.Op = Op
        self.status.Q_k = reg_k.to_be_write
        if type(reg_j) == int:
            if Op != Operation.STORE:
                dest.to_be_write = True
            else:
                self.status.write_mem = not dest.to_be_write
        else:
            self.status.Q_j = reg_j.to_be_write
            if Op != Operation.BNE:
                dest.to_be_write = True

    def get_info_str(self) -> str:
        info = ""
        for stage, clock in self.stage_clocks.items():
            info += f"{clock:>6}" if clock is not None else " " * 6
        info += (
            f' | {"Yes" if self.status.Q_j else "No":<3} {"Yes" if self.status.Q_k else "No":<3} {self.stage.value:<9}'
        )
        return info

    def __format__(self, __format_spec: str) -> str:
        dest_name = self.dest if type(self.dest) == str else self.dest.name
        info = f"{self.Op.name:<5} {dest_name:<4} {self.j if type(self.j) == int else self.j.name:>2} {self.k.name:>2}"
        return format(info, __format_spec)


class CDB:
    def __init__(self, number=2) -> None:
        self.number = number
        self.available: bool = True
        self.left_available_cdb = self.number

    def send_data(self):
        assert self.available
        self.left_available_cdb -= 1
        if self.left_available_cdb == 0:
            self.available = False

    def finish_write_back(self):
        self.left_available_cdb = self.number
        self.available = True


class SuperScale:
    def __init__(self, rg: RegisterGroup, multi_issue_number: int = 2, cdb_number: int = 2) -> None:
        self.register_group = rg
        self.multi_issue_number = multi_issue_number  # 超标量个数
        self.CDB = CDB(cdb_number)
        self.instructions: List[Instruction] = []
        self.pc: int = 0
        self.functional_units: List[Unit] = [
            # Unit(name="Address Adder", function=UnitFunction.INTEGER, CDB=self.CDB),
            Unit(name="Integer ALU", function=UnitFunction.ADD, CDB=self.CDB),
            Unit(name="FP ALU", function=UnitFunction.FADD, CDB=self.CDB),
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
            # 当全部指令都完成后退出
            if self.pc >= instruction_length:
                complete_instruction_number = 0
                for instruction in self.instructions:
                    if instruction.stage == InstructionStage.COMPLETE:
                        complete_instruction_number += 1
                if complete_instruction_number == instruction_length:
                    break

            # 多发射新指令
            if self.pc != instruction_length:
                branch_operators = [Operation.BNE]
                for _ in range(self.multi_issue_number):
                    instruction = self.instructions[self.pc]
                    unit = self.get_unit(instruction.unit_function)
                    # 给指令绑定 unit, 暂时不将 unit 绑定指令, 在 issue 阶段绑定
                    instruction.unit = unit
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
            for instruction in self.issued_instructions:
                if instruction.stage == InstructionStage.EXEC and instruction.left_latency == 0:
                    instruction.unit.in_use = False
                if instruction.stage == InstructionStage.WRITE:
                    # 对于
                    for unit in self.functional_units:
                        if unit.in_use:
                            if unit.status.Q_j and unit.instruction.j == instruction.dest:
                                unit.status.Q_j = False
                            if unit.status.Q_k and unit.instruction.k == instruction.dest:
                                unit.status.Q_k = False

            self.CDB.finish_write_back()

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
        print(f"    Instructions     | Issue  Exec   Mem Write | Qj  Qk  stage      | Comment")
        for instruction in self.instructions:
            print(f"    {instruction:<17}", end="|")
            print(instruction.get_info_str())
        print("\n")
        print("[register result status]\n")
        print(self.register_group)
        print("\n")


def main():
    rg = RegisterGroup()
    rg.R1.value = 200
    rg.R2.value = 300

    instructions = [
        # loop1
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.LOAD, dest=rg.F0, j=0, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.FADD, dest=rg.F4, j=rg.F0, k=rg.F2, unit_function=UnitFunction.FADD, latency=3),
        Instruction(Op=Operation.STORE, dest=rg.F4, j=0, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.ADD, dest=rg.R1, j=-8, k=rg.R1, unit_function=UnitFunction.ADD),
        Instruction(Op=Operation.BNE, dest="Loop", j=rg.R1, k=rg.R2, unit_function=UnitFunction.ADD),
    ]

    isa = SuperScale(rg, multi_issue_number=2, cdb_number=2)
    isa.load_instructions(instructions)
    isa.run()


if __name__ == "__main__":
    main()
