from enum import Enum
from typing import List


# RISCV-32I 6 种类型
class OpCode(Enum):
    R = "0110011"
    I_JALR = "1100111"
    I_CALC = "0010011"
    I_LOAD = "0000011"
    S = "0100011"
    B = "1100011"
    U_LUI = "0110111"
    U_AUIPC = "0010111"
    J = "1101111"


# 部分 I 型指令
class IFunct3(Enum):
    ADDI = "000"
    SLTI = "010"
    SLTIU = "011"
    XORI = "100"
    ORI = "110"
    ANDI = "111"
    SLLI = "001"
    SRLI = "101"
    SRAI = "101"
    JALR = "000"
    LB = "000"
    LH = "001"
    LW = "010"
    LBU = "100"
    LHU = "101"


# 部分 S 型指令
class SFunct3(Enum):
    SB = "000"  # 本次需要
    SH = "001"
    SW = "010"


# B 型指令
class BFunct3(Enum):
    BEQ = "000"
    BNE = "001"
    BLT = "100"
    BGE = "101"
    BLTU = "110"
    BGEU = "111"


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
    SRA = "0100000"


class InstructionInfo:
    opcode: OpCode
    rs1: int
    rs2: int
    rd: int
    funct3: Enum
    funct7: Enum
    imm: int


class PipeReg:
    rs1: int
    rs2: int
    value: int
    mem_value: int


class Instruction:
    def __init__(self, isa: "ISA") -> None:
        self.isa = isa

    def stage_ex(self):
        """
        EX-执行.对指令的各种操作数进行运算

        IF ID 阶段操作相对固定, EX MEM WB 阶段需要根据具体指令在做调整

        单指令可以继承 Instruction 类并重写此方法
        """

    def stage_mem(self):
        """
        MEM-存储器访问.将数据写入存储器或从存储器中读出数据

        单指令可以继承 Instruction 类并重写此方法
        """

    def stage_wb(self):
        """
        WB-写回.将指令运算结果存入指定的寄存器

        单指令可以继承 Instruction 类并重写此方法
        """


class ISA:
    """
    基础处理器架构
    """

    def __init__(self) -> None:
        self.pc = 0
        self.registers = [0] * 32
        self.memory = [0] * 512
        self.instruction: Instruction = None  # 当前指令
        self.instructions: List[str] = None  # 导入的指令集
        self.instruction_info = InstructionInfo()  # 当前指令的信息拆分
        self.pipeline_register = PipeReg()

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
        self.instruction = self.instructions[self.pc]
        self.pc += 1

    def stage_id(self):
        """
        ID-译码 解析指令并读取寄存器的值"""
        # raise NotImplementedError("should implement stage ID")

    def stage_exe(self):
        """
        EX-执行.对指令的各种操作数进行运算
        """
        self.instruction.stage_ex()

    def stage_mem(self):
        """
        MEM-存储器访问.将数据写入存储器或从存储器中读出数据
        """
        self.instruction.stage_mem()

    def stage_wb(self):
        """
        WB-写回.将指令运算结果存入指定的寄存器
        """
        self.instruction.stage_wb()

    def show_info(self, info=None):
        mem_range = 5
        register_range = 4

        if info is not None:
            print(info)
        print("#" * 20)
        for i in range(mem_range):
            print(f"mem[{i}] = {self.memory[i]}")
        print("#" * 20)
        for i in range(register_range):
            print(f"r{i} = {self.registers[i]}")
        print("#" * 20)
