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


class IR:
    '''
    intermediate register
    '''
    rs1: int
    rs2: int
    value: int
    mem_value: int


class Instruction:
    def __init__(self, isa: "ISA") -> None:
        self.isa = isa
        self.pc_inc = True
        # print(self.__class__.__name__)

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
        if self.pc_inc:
            self.isa.pc += 4


class ISA:
    """
    基础处理器架构
    """

    def __init__(self) -> None:
        # 基础配置信息
        register_number = 32
        memory_range = 0x200

        self.pc = 0
        self.registers = [0] * register_number  # 寄存器组
        self.memory = [0] * memory_range  # 内存
        self.instruction: Instruction = None  # 当前指令
        self.instruction_info = InstructionInfo()  # 当前指令的信息拆分
        self.IR = IR()

    def load_instructions(self, instructions, pc=0x100):
        self.pc = pc
        # 小端存储
        for inst in instructions:
            instruction_str = format(inst, "032b")
            self.memory[pc + 3] = int(instruction_str[:8], 2)
            self.memory[pc + 2] = int(instruction_str[8:16], 2)
            self.memory[pc + 1] = int(instruction_str[16:24], 2)
            self.memory[pc] = int(instruction_str[24:], 2)
            pc += 4

    def run(self):
        while True:
            self.stage_if()
            if self.pc == -1:
                break
            self.stage_id()
            self.stage_ex()
            self.stage_mem()
            self.stage_wb()

    def stage_if(self):
        """
        IF-取指令.根据PC中的地址在指令存储器中取出一条指令
        """
        # 小端取数
        self.instruction = ""
        self.instruction += format(self.memory[self.pc + 3], "08b")
        self.instruction += format(self.memory[self.pc + 2], "08b")
        self.instruction += format(self.memory[self.pc + 1], "08b")
        self.instruction += format(self.memory[self.pc], "08b")

        # 全 0 默认运行完所有指令, 退出
        if int(self.instruction) == 0:
            self.pc = -1

    def stage_id(self):
        """
        ID-译码 解析指令并读取寄存器的值"""
        raise NotImplementedError("should implement stage ID")

    def stage_ex(self):
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
                print(f"mem[{index:2}] = [{self.memory[index]:3}]", end=" ")
            print("")
        print("#" * 20)
        for i in range(register_range // register_align):
            for j in range(register_align):
                index = i * register_align + j
                print(f"r{index:<2} = [{self.registers[index]:3}]", end=" ")
            print("")
        print("#" * 20)

    def binary_str(self, imm: str):
        """
        取补码计算, 如果首位为 0 则直接计算值, 如果为 1 则 01 取反加一
        """
        if imm[0] == "1":
            inverted_str = "".join("1" if bit == "0" else "0" for bit in imm)
            abs_value = int(inverted_str, 2) + 1
            return -abs_value
        else:
            return int(imm, 2)
