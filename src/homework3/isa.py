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
        self.is_locked = False
        self.class_name = self.__class__.__name__

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


class ControlSignal:
    """
    控制信号, 决策对应 MUX 应该选择使用哪一个作为输入
    """
    ALUop: int  # ALU 如何进行计算
    RegWrite: bool  # 是否写寄存器
    ALUsrc: int  # ALU 的第二个输入选择哪一个
    MemWrite: int  # 是否写内存
    MemRead: int  # 是否读内存
    MemtoReg: int  # 选择写回寄存器的值
    PCsrc: int  # 选择更新 PC 的方式


class IF_ID:
    instruction: str


class ID_EX:
    rs1: int
    rs2: int
    ra: int
    rb: int
    rd: int
    imm: int
    ctl_sig: ControlSignal


class EX_MEM:
    result: int
    data: int
    ctl_sig: ControlSignal


class MEM_WB:
    ...


class IR(Component):
    """
    中间寄存器, 用于存储流水线 5 阶段的 4 个中间阶段的执行结果
    """

    def __init__(self) -> None:
        super().__init__()
        self.IF_ID = IF_ID()
        self.ID_EX = ID_EX()
        self.EX_MEM = EX_MEM()
        self.MEM_WB = MEM_WB()

        self.pre_IF_ID = IF_ID()
        self.pre_ID_EX = ID_EX()
        self.pre_EX_MEM = EX_MEM()
        self.pre_MEM_WB = MEM_WB()

    def update(self):
        self.IF_ID = self.pre_IF_ID
        self.ID_EX = self.pre_ID_EX
        self.EX_MEM = self.pre_EX_MEM
        self.MEM_WB = self.pre_MEM_WB

    def is_empty(self):
        ...

class Instruction:
    def __init__(self, isa: "PipelineISA") -> None:
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


class RegisterGroup(Component):
    def __init__(self, number=32) -> None:
        super().__init__()
        self.registers = [0] * number

    def read(self, rs1: int, rs2: int) -> (int, int):
        """
        读取对应寄存器的值
        """
        self.lock()
        ra = None
        rb = None
        if rs1 is not None:
            ra = self.registers[rs1]
        if rs2 is not None:
            rb = self.registers[rs2]
        self.unlock()
        return ra, rb

    def write(self, rd: int, value: int, RegWrite: ControlSignal.RegWrite):
        """
        只有当 RegWrite 信号为 1 才可以写入寄存器
        """
        if RegWrite is True:
            self.lock()
            self.registers[rd] = value
            self.unlock()


class Memory(Component):
    def __init__(self, addr_range=0x200) -> None:
        super().__init__()
        self.memory = [0] * addr_range

    def read(self, addr: int, MemRead: ControlSignal.MemRead):
        if MemRead is True:
            self.lock()
            value = self.memory[addr]
            self.unlock()
            return value

    def write(self, addr: int, value: int, MemWrite: ControlSignal.MemWrite):
        if MemWrite is True:
            self.lock()
            self.memory[addr] = value
            self.unlock()


class PipelineISA:
    """
    流水线处理器架构

    正常来说 5 阶段流水线是同步执行的, 通用寄存器组和存储器在时钟上升沿写入,IR和中间寄存器在时钟下降沿写入
    考虑到 Python 没有办法做到电路级模拟, 理论上来说如果想要实现时序级模拟, 需要使用 5 个线程和 5 把锁,
    以保证当前阶段写入IR和中间寄存器之前该寄存器的值已经被下一个阶段读取

    但实际上可以利用 IR 作为中间变量, 将 **写更新** 和 **读 + 执行** 区分开, 采用串行的方式模拟流水线
    """

    def __init__(self) -> None:
        # 基础配置信息
        register_number = 32
        addr_range = 0x200

        self.pc = 0
        self.registers = RegisterGroup(register_number)  # 寄存器组
        self.memory = Memory(addr_range)  # 内存
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
            # stage_if ~ stage_wb 阶段的写入IR并不是真正的写入
            # 此时的才是真正的更新流水线阶段需要使用的 IR 的值
            self.IR.update()

            self.stage_if()
            # 当取指之后, 流水线 IR 全空且指令也为 0, 则说明已经流水线全部结束且没有新指令了
            if self.IR.is_empty():
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
        self.IR.pre_IF_ID.instruction = ""
        self.IR.pre_IF_ID.instruction += format(self.memory[self.pc + 3], "08b")
        self.IR.pre_IF_ID.instruction += format(self.memory[self.pc + 2], "08b")
        self.IR.pre_IF_ID.instruction += format(self.memory[self.pc + 1], "08b")
        self.IR.pre_IF_ID.instruction += format(self.memory[self.pc], "08b")

    def stage_id(self):
        """
        ID-译码 解析指令并读取寄存器的值
        """
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
