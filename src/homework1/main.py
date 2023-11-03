from enum import Enum

# RISCV 32I 指令集介绍可以参考
# https://www.sunnychen.top/archives/riscvbasic


# RISCV-32I 6 种类型
class OpCode(Enum):
    R = "0110011"
    I = "0000011"
    S = "0100011"
    B = "1100011"
    U = "0010111"
    J = "1100111"


# 部分 I 型指令
class IFunct3(Enum):
    LB = "000"  # 本次需要
    LH = "001"
    LW = "010"
    LBU = "100"
    LHU = "101"


# 部分 S 型指令
class SFunct3(Enum):
    SB = "000"  # 本次需要
    SH = "001"
    SW = "010"


# 部分 R 型指令
class RFunct3(Enum):
    ADD = "000"  # 本次需要
    SUB = "000"
    SLL = "001"
    SLT = "010"
    SLTU = "011"
    XOR = "100"
    SRL = "101"
    SRA = "101"
    OR = "110"
    AND = "111"


class RFunct7(Enum):
    ADD = "0000000"
    SUB = "0100000"
    XOR = "0000000"


class InstructionInfo:
    opcode: OpCode
    rs1: int
    rs2: int
    rd: int
    funct3: Enum
    funct7: Enum
    imm: int


class IR:
    """
    intermediate register
    """

    rs1: int
    rs2: int
    value: int
    mem_value: int


class ISA:
    """
    RISCV 32I 单周期五阶段

    仅作对于 LB SB XOR ADD 的支持
    """

    def __init__(self) -> None:
        self.pc = 0
        self.registers = [0] * 32
        self.memory = [0] * 512
        self.current_instruction = None  # 当前指令
        self.instructions = None  # 导入的指令集
        self.instruction_info = None  # 当前指令的信息拆分
        self.IR = IR()

    def load_instructions(self, instructions):
        self.instructions = instructions
        self.pc = 0

    def run(self):
        instructions_length = len(self.instructions)
        while True:
            self.stage_if()
            self.stage_id()
            self.stage_exe()
            self.stage_mem()
            self.stage_wb()
            if self.pc >= instructions_length:
                break

    def stage_if(self):
        """
        IF-取指令.根据PC中的地址在指令存储器中取出一条指令
        """
        self.current_instruction = self.instructions[self.pc]
        self.pc += 1

    def stage_id(self):
        """
        ID-指令译码.由取出的指令生成各种控制信号,明确该指令要进行的行为
        """
        instruction_info = InstructionInfo()
        opcode = self.current_instruction[-7:]
        opcode_type = OpCode(opcode)
        instruction_info.opcode = opcode_type
        if opcode_type == OpCode.R:
            # xor
            # add
            instruction_info.funct7 = RFunct7(self.current_instruction[:7])
            instruction_info.rs2 = int(self.current_instruction[7:12], 2)
            instruction_info.rs1 = int(self.current_instruction[12:17], 2)
            instruction_info.funct3 = RFunct3(self.current_instruction[17:20])
            instruction_info.rd = int(self.current_instruction[20:25], 2)
            instruction_info.imm = None
        elif opcode_type == OpCode.I:
            # lb
            instruction_info.funct7 = None
            instruction_info.rs2 = None
            instruction_info.rs1 = int(self.current_instruction[12:17], 2)
            instruction_info.funct3 = IFunct3(self.current_instruction[17:20])
            instruction_info.rd = int(self.current_instruction[20:25], 2)
            instruction_info.imm = int(self.current_instruction[:12], 2)
        elif opcode_type == OpCode.S:
            # sb
            instruction_info.funct7 = None
            instruction_info.rs2 = int(self.current_instruction[7:12], 2)
            instruction_info.rs1 = int(self.current_instruction[12:17], 2)
            instruction_info.funct3 = SFunct3(self.current_instruction[17:20])
            instruction_info.rd = None
            instruction_info.imm = int(
                self.current_instruction[:7] + self.current_instruction[20:25], 2
            )
        else:
            raise ValueError("unsupported opcode type in this homework!")

        self.instruction_info = instruction_info

        if self.instruction_info.rs1 is not None:
            self.IR.rs1 = self.registers[self.instruction_info.rs1]

        if self.instruction_info.rs2 is not None:
            self.IR.rs2 = self.registers[self.instruction_info.rs2]

    def stage_exe(self):
        """
        EX-执行.对指令的各种操作数进行运算
        """
        if self.instruction_info.funct3 == RFunct3.XOR:
            self.IR.value = self.IR.rs1 ^ self.IR.rs2
        elif self.instruction_info.funct3 == RFunct3.ADD:
            self.IR.value = self.IR.rs1 + self.IR.rs2
        elif self.instruction_info.funct3 in (IFunct3.LB, SFunct3.SB):
            self.IR.value = self.IR.rs1 + self.instruction_info.imm
        else:
            pass

    def stage_mem(self):
        """
        MEM-存储器访问.将数据写入存储器或从存储器中读出数据
        """
        if self.instruction_info.funct3 == IFunct3.LB:
            self.IR.mem_value = self.memory[self.IR.value]
        else:
            pass

    def stage_wb(self):
        """
        WB-写回.将指令运算结果存入指定的寄存器
        """
        if self.instruction_info.funct3 == RFunct3.XOR:
            self.registers[self.instruction_info.rd] = self.IR.value
        elif self.instruction_info.funct3 == RFunct3.ADD:
            self.registers[self.instruction_info.rd] = self.IR.value
        elif self.instruction_info.funct3 == SFunct3.SB:
            self.memory[self.IR.value] = self.IR.rs2
        elif self.instruction_info.funct3 == IFunct3.LB:
            self.registers[self.instruction_info.rd] = self.IR.mem_value
        else:
            pass

    def show_info(self, info=None):
        mem_range = 20
        mem_align = 4
        register_range = 32
        register_align = 8

        if info is not None:
            print(info)
        print("#" * 20)
        for i in range(mem_range // mem_align):
            for j in range(mem_align):
                index = i * mem_align + j
                print(f"mem[{index:2}] = {self.memory[index]:3}", end=" |")
            print("")
        print("#" * 20)
        for i in range(register_range // register_align):
            for j in range(register_align):
                index = i * register_align + j
                print(f"r{index:<2} = {self.registers[index]:3}", end=" |")
            print("")
        print("#" * 20)


def main():
    # xor r1, r1, r1
    # lb 0(r1), r2
    # lb 1(r1), r3
    # add r2, r3, r3
    # sb 3(r1), r3

    instructions = [
        # 31 ---------------------------0
        "00000000000100001100000010110011",
        "00000000000000001000000100000011",
        "00000000000100001000000110000011",
        "00000000001100010000000110110011",
        "00000000001100001000000110100011",
    ]

    isa = ISA()
    isa.memory[0] = 123
    isa.memory[1] = 99
    isa.show_info("before")

    isa.load_instructions(instructions)
    isa.run()
    isa.show_info("after")


if __name__ == "__main__":
    main()
