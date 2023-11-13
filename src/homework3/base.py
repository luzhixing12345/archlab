from enum import Enum


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
class I_CALCFunct3(Enum):
    ADDI = "000"
    SLTI = "010"
    SLTIU = "011"
    XORI = "100"
    ORI = "110"
    ANDI = "111"
    SLLI = "001"
    SRLI = "101"
    SRAI = "101"


class I_JALRFunct3(Enum):
    JALR = "000"


class I_LOADFunct3(Enum):
    LB = "000"
    LH = "001"
    LW = "010"
    LBU = "100"
    LHU = "101"


# 部分 S 型指令
class SFunct3(Enum):
    SB = "000"
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
    ADD = "000"
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


class Component:
    """
    元件基类, 所有其他处理器设计元件都需要继承此类

    用于性能记录
    """

    def __init__(self) -> None:
        self.class_name = self.__class__.__name__

        self.is_locked = False
        self.is_empty = True

    def lock(self):
        if self.is_locked:
            print(f"{self.class_name} is locked")
            exit(1)
        self.is_locked = True

    def unlock(self):
        if not self.is_locked:
            print(f"try to unlock a not locked lock in {self.class_name}")
            exit(1)
        self.is_locked = False


class ALUop(Enum):
    ADD = 0b0000
    SUB = 0b1000
    LSHIFT = 0b0001
    # LSHIFT_ = 0b1001
    OUTPUT_B = 0b0011  # 选择 B 结果直接输出
    # B_ = 0b1011
    XOR = 0b0100
    # XOR_ = 0b1100
    LRSHIFT = 0b0101
    ARSHIFT = 0b1101
    OR = 0b0110
    # OR_ = 0b1110
    AND = 0b0111
    # AND_ = 0b1111


class ALU_Asrc(Enum):
    RA = 0
    PC = 1


class ALU_Bsrc(Enum):
    RB = 0
    IMM = 1
    NEXT = 2  # pc + 4


class PCsrc(Enum):
    PC = 0
    IMM = 1
    JAL = 2
    JALR = 3
    AUIPC = 4


class MemtoReg(Enum):
    READ_DATA = 0
    ALU_RESULT = 1


class MemOp(Enum):
    NONE = 0b111
    SIGN1 = 0b000
    SIGN2 = 0b001
    SIGN4 = 0b010
    UNSIGN1 = 0b100
    UNSIGN2 = 0b101


class ControlSignal:
    """
    控制信号, 决策对应 MUX 应该选择使用哪一个作为输入
    """

    ALU_Asrc: ALU_Asrc # ALU 的第一个输入选择哪一个
    ALU_Bsrc: ALU_Bsrc  # ALU 的第二个输入选择哪一个
    ALUop: ALUop  # ALU 如何进行计算
    RegWrite: bool  # 是否写寄存器
    MemRead: bool  # 是否读内存
    MemWrite: bool  # 是否写内存
    MemtoReg: MemtoReg  # 写回寄存器的值选择哪一个
    MemOp: MemOp  # 读取内存的方式
    PCsrc: PCsrc  # 如何更新 PC


class IF_ID(Component):
    instruction: str
    pc: int


class ID_EX(Component):
    ra: int
    rb: int
    rd: int
    imm: int
    ctl_sig: ControlSignal
    # 条件跳转的方式, 只对于 B 指令在 EX 阶段使用
    Branch: BFunct3

    # 存 rs1 和 rs2 是为了在 EX 阶段检测数据冒险
    rs1: int
    rs2: int
    pc: int


class EX_MEM(Component):
    alu_result: int
    rb: int
    rd: int
    MemRead: bool
    MemWrite: bool
    MemtoReg: MemtoReg
    MemOp: MemOp
    RegWrite: bool
    
    # 条件跳转是否成立
    branch_cond: bool
    PCsrc: PCsrc
    pc: int
    imm: int

class MEM_WB(Component):
    rd: int
    read_data: int
    alu_result: int
    MemtoReg: MemtoReg
    RegWrite: bool
