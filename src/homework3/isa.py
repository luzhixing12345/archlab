from base import *
from instructions import *
import copy


class IR(Component):
    """
    中间寄存器, 用于存储流水线 5 阶段的 4 个中间阶段的执行结果

    ISA 执行 run 时会从前一阶段的 IF_ID 取值, 并将结果写入到下一阶段的 pre_ID_EXE 中, 以此类推
    全部执行结束后会调用 update 将所有 pre_IR 的结果更新到 IR 中

    相当于采用了双倍的硬件/空间
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

        self.bubble = False

    def update(self):
        if self.bubble:
            self.EX_MEM.is_empty = True
            self.MEM_WB = copy.deepcopy(self.pre_MEM_WB)
        else:
            self.IF_ID = copy.deepcopy(self.pre_IF_ID)
            self.ID_EX = copy.deepcopy(self.pre_ID_EX)
            self.EX_MEM = copy.deepcopy(self.pre_EX_MEM)
            self.MEM_WB = copy.deepcopy(self.pre_MEM_WB)

        self.bubble = False

    def is_flushed(self):
        """
        当 pre_IF_ID 取指为空, 且所有阶段的 IR 均空, 终止流水线
        """
        return (
            self.pre_IF_ID.is_empty
            and self.IF_ID.is_empty
            and self.ID_EX.is_empty
            and self.EX_MEM.is_empty
            and self.MEM_WB.is_empty
        )

    def reset(self):
        self.IF_ID = IF_ID()
        self.ID_EX = ID_EX()
        self.EX_MEM = EX_MEM()
        self.MEM_WB = MEM_WB()

        self.pre_IF_ID = IF_ID()
        self.pre_ID_EX = ID_EX()
        self.pre_EX_MEM = EX_MEM()
        self.pre_MEM_WB = MEM_WB()

        self.bubble = False


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

    def write(self, rd: int, write_data: int, RegWrite: bool):
        """
        只有当 RegWrite 信号为 1 才可以写入寄存器
        """
        if RegWrite is True:
            self.lock()
            self.registers[rd] = write_data
            self.unlock()

    def reset(self):
        """
        重置寄存器状态, 归零
        """
        for i in range(len(self.registers)):
            self.registers[i] = 0

    def __setitem__(self, index, value):
        self.registers[index] = value

    def __getitem__(self, index):
        return self.registers[index]


class Memory(Component):
    def __init__(self, addr_range=0x200) -> None:
        super().__init__()
        self.memory = [0] * addr_range

    def read(self, addr: int, MemRead: bool, op: Enum):
        if MemRead is True:
            self.lock()
            if op == MemOp.SIGN1:
                value = self.memory[addr]
            elif op == MemOp.SIGN2:
                value = self.memory[addr]
                value += self.memory[addr + 1] << 8
            elif op == MemOp.SIGN4:
                value = self.memory[addr]
                value += self.memory[addr + 1] << 8
                value += self.memory[addr + 2] << 16
                value += self.memory[addr + 3] << 24
            else:
                raise ValueError()
            self.unlock()
            return value

    def write(self, addr: int, write_data: int, MemWrite: bool, op: Enum):
        if MemWrite is True:
            self.lock()
            if op == MemOp.SIGN1:
                self.memory[addr] = write_data
            elif op == MemOp.SIGN2:
                self.memory[addr] = write_data & 0xFF
                self.memory[addr + 1] = write_data & 0xFF00
            elif op == MemOp.SIGN4:
                self.memory[addr] = write_data & 0xFF
                self.memory[addr + 1] = write_data & 0xFF00
                self.memory[addr + 2] = write_data & 0xFF0000
                self.memory[addr + 3] = write_data & 0xFF000000
            else:
                raise ValueError()
            self.unlock()

    def reset(self):
        """
        重置内存状态, 归零
        """
        for i in range(len(self.memory)):
            self.memory[i] = 0

    def __setitem__(self, index, value):
        self.memory[index] = value

    def __getitem__(self, index):
        return self.memory[index]


class ALU(Component):
    def __init__(self, op: Enum = None) -> None:
        super().__init__()
        # 设置 op 表示某一类特定的功能
        # 比如 ID_adder 只做加法
        self.op = op

    def calc(self, input_a: int, input_b: int, op: Enum = None) -> int:
        if op is None:
            op = self.op
        if op == ALUop.ADD:
            return input_a + input_b
        elif op == ALUop.SUB:
            return input_a - input_b
        elif op == ALUop.LSHIFT:
            return input_a << input_b
        elif op == ALUop.OUTPUT_B:
            return input_b
        elif op == ALUop.XOR:
            return input_a ^ input_b
        elif op == ALUop.LRSHIFT:
            return (input_a & 0xFFFFFFFF) >> input_b
        elif op == ALUop.ARSHIFT:
            return input_a >> input_b
        elif op == ALUop.OR:
            return input_a | input_b
        elif op == ALUop.AND:
            return input_a & input_b
        else:
            raise ValueError(f"unknown ALU operator value {op}")


class PipelineISA:
    """
    流水线处理器架构

    正常来说 5 阶段流水线是同步执行的, 通用寄存器组和存储器在时钟上升沿写入,IR和中间寄存器在时钟下降沿写入
    考虑到 Python 没有办法做到电路级模拟, 理论上来说如果想要实现时序级模拟, 需要使用 5 个线程和 5 把锁,
    以保证当前阶段写入IR和中间寄存器之前该寄存器的值已经被下一个阶段读取

    但实际上可以利用 IR 作为中间变量, 从 IF_ID 中读取, 写入到 pre_ID_EX 中, 最后同步更新所有的 IR,
    这样就实现了采用串行的方式模拟流水线
    """

    def __init__(self) -> None:
        # 基础配置信息
        register_number = 32
        addr_range = 0x2000

        self.pc = 0
        self.registers = RegisterGroup(register_number)  # 寄存器组
        self.memory = Memory(addr_range)  # 内存
        self.ALU = ALU()
        self.IR = IR()

        self.ID_adder = ALU(ALUop.ADD)  # 加法器, 用于计算 ID 阶段的 PC + IMM
        self.ID_subtractor = ALU(ALUop.SUB)  # 减法器, 用于计算比较

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

    def reset(self):
        """
        重置处理器状态, 用于多次运行
        """
        self.pc = 0
        self.registers.reset()
        self.memory.reset()
        self.IR.reset()

    def run(self):
        self.step = 0
        while True:
            self.step += 1
            # stage_if ~ stage_wb 阶段的写入IR并不是真正的写入
            # 此时的才是真正的更新流水线阶段需要使用的 IR 的值
            self.IR.update()

            # 优先写回
            self.stage_wb()
            self.stage_if()
            # 当取指之后, 流水线 IR 全空且新指令也为 0, 则说明已经流水线全部结束且没有新指令了
            if self.IR.is_flushed():
                break
            self.stage_id()
            self.stage_ex()
            self.stage_mem()
            self.update_pc()
            # self.show_info()

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

        # 保存当前指令对应 PC 值, 以供 ID 阶段的 B/J 型指令计算跳转地址
        self.IR.pre_IF_ID.pc = self.pc

        if int(self.IR.pre_IF_ID.instruction) == 0:
            self.IR.pre_IF_ID.is_empty = True
        else:
            self.IR.pre_IF_ID.is_empty = False

    def stage_id(self):
        """
        ID-译码 解析指令并读取寄存器的值
        """
        if self.IR.IF_ID.is_empty:
            # IF_ID 的 IR 为空, 跳过 ID 阶段, 并设置下一阶段的 IR 也为空
            self.IR.pre_ID_EX.is_empty = True
            return
        else:
            self.IR.pre_ID_EX.is_empty = False

        instruction = self.IR.IF_ID.instruction
        instruction_info = InstructionInfo()

        opcode_type = OpCode(instruction[-7:])
        instruction_info.opcode = opcode_type
        if opcode_type == OpCode.R:
            instruction_info.funct7 = RFunct7(instruction[:7])
            instruction_info.rs2 = int(instruction[7:12], 2)
            instruction_info.rs1 = int(instruction[12:17], 2)
            instruction_info.funct3 = RFunct3(instruction[17:20])
            instruction_info.rd = int(instruction[20:25], 2)
            instruction_info.imm = None
        elif opcode_type in (OpCode.I_LOAD, OpCode.I_CALC, OpCode.I_JALR):
            instruction_info.funct7 = None
            instruction_info.rs2 = None
            instruction_info.rs1 = int(instruction[12:17], 2)
            funct3 = {
                OpCode.I_LOAD: I_LOADFunct3,
                OpCode.I_CALC: I_CALCFunct3,
                OpCode.I_JALR: I_JALRFunct3,
            }
            instruction_info.funct3 = funct3[opcode_type](instruction[17:20])
            instruction_info.rd = int(instruction[20:25], 2)
            instruction_info.imm = self.binary_str(instruction[:12])

        elif opcode_type == OpCode.S:
            instruction_info.funct7 = None
            instruction_info.rs2 = int(instruction[7:12], 2)
            instruction_info.rs1 = int(instruction[12:17], 2)
            instruction_info.funct3 = SFunct3(instruction[17:20])
            instruction_info.rd = None
            instruction_info.imm = self.binary_str(instruction[:7] + instruction[20:25])
        elif opcode_type == OpCode.B:
            instruction_info.funct7 = None
            instruction_info.rs2 = int(instruction[7:12], 2)
            instruction_info.rs1 = int(instruction[12:17], 2)
            instruction_info.funct3 = BFunct3(instruction[17:20])
            instruction_info.rd = None
            instruction_info.imm = self.binary_str(
                instruction[0] + instruction[24] + instruction[1:7] + instruction[20:24] + "0"
            )

        elif opcode_type in (OpCode.U_AUIPC, OpCode.U_LUI):
            instruction_info.funct7 = None
            instruction_info.rs2 = None
            instruction_info.rs1 = None
            instruction_info.funct3 = None
            instruction_info.rd = int(instruction[20:25], 2)
            instruction_info.imm = self.binary_str(instruction[:20] + "0" * 12)
        elif opcode_type == OpCode.J:
            instruction_info.funct7 = None
            instruction_info.rs2 = None
            instruction_info.rs1 = None
            instruction_info.funct3 = None
            instruction_info.rd = int(instruction[20:25], 2)
            instruction_info.imm = self.binary_str(
                instruction[0] + instruction[12:20] + instruction[11] + instruction[1:11] + "0"
            )
        else:
            raise ValueError("unknown opcode type")

        self.IR.pre_ID_EX.ra, self.IR.pre_ID_EX.rb = self.registers.read(
            instruction_info.rs1, instruction_info.rs2
        )
        self.IR.pre_ID_EX.rd = instruction_info.rd
        self.IR.pre_ID_EX.imm = instruction_info.imm
        self.IR.pre_ID_EX.ctl_sig = self.get_control_signal(instruction_info)

        self.IR.pre_ID_EX.rs1 = instruction_info.rs1
        self.IR.pre_ID_EX.rs2 = instruction_info.rs2
        self.IR.pre_ID_EX.pc = self.IR.IF_ID.pc

        if opcode_type == OpCode.B:
            # B 类型单独设置 Branch 标记位用于 update_pc 阶段计算
            # 需要根据 Branch 的类型来   判断跳转条件是否成立
            self.IR.pre_ID_EX.Branch = instruction_info.funct3
        else:
            self.IR.pre_ID_EX.Branch = None

    def get_control_signal(self, instruction_info: InstructionInfo) -> ControlSignal:
        RISCV_32I_instructions = {
            OpCode.R: {
                RFunct3.ADD: R_ADD,
                # RFunct3.SUB: R_SUB,
                RFunct3.SLL: R_SLL,
                RFunct3.SLT: R_SLT,
                RFunct3.SLTU: R_SLTU,
                RFunct3.XOR: R_XOR,
                RFunct3.SRL: R_SRL,
                RFunct3.SRA: R_SRA,
                RFunct3.OR: R_OR,
                RFunct3.AND: R_AND,
            },
            OpCode.I_CALC: {
                I_CALCFunct3.ADDI: I_ADDI,
                I_CALCFunct3.SLTI: I_SLTI,
                I_CALCFunct3.SLTIU: I_SLTIU,
                I_CALCFunct3.XORI: I_XORI,
                I_CALCFunct3.ORI: I_ORI,
                I_CALCFunct3.ANDI: I_ANDI,
                I_CALCFunct3.SLLI: I_SLLI,
                I_CALCFunct3.SRLI: I_SRLI,
                I_CALCFunct3.SRAI: I_SRAI,
            },
            OpCode.I_JALR: {I_JALRFunct3.JALR: I_JALR},
            OpCode.I_LOAD: {
                I_LOADFunct3.LB: I_LB,
                I_LOADFunct3.LH: I_LH,
                I_LOADFunct3.LW: I_LW,
                I_LOADFunct3.LBU: I_LBU,
                I_LOADFunct3.LHU: I_LHU,
            },
            OpCode.S: {SFunct3.SB: S_SB, SFunct3.SH: S_SH, SFunct3.SW: S_SW},
            OpCode.B: {
                BFunct3.BEQ: B_BEQ,
                BFunct3.BNE: B_BNE,
                BFunct3.BLT: B_BLT,
                BFunct3.BGE: B_BGE,
                BFunct3.BLTU: B_BLTU,
                BFunct3.BGEU: B_BGEU,
            },
        }

        # 一些特殊情况的处理, 单独判断
        if instruction_info.funct3 == RFunct3.ADD and instruction_info.funct7 == RFunct7.SUB:
            # ADD/SUB 的 funct3 相同
            instruction = R_SUB
        elif instruction_info.funct3 == RFunct3.SRL and instruction_info.funct7 == RFunct7.SRA:
            # SRL SRA
            instruction = R_SRA
        elif instruction_info.opcode == OpCode.U_AUIPC:
            instruction = U_AUIPC
        elif instruction_info.opcode == OpCode.U_LUI:
            instruction = U_LUI
        elif instruction_info.opcode == OpCode.J:
            instruction = J_JAL
        else:
            instruction = RISCV_32I_instructions[instruction_info.opcode][instruction_info.funct3]

        return instruction().get_control_signal()

    def stage_ex(self):
        """
        EX-执行.对指令的各种操作数进行运算
        """
        if self.IR.ID_EX.is_empty:
            # ID_EX 的 IR 为空, 跳过 EX 阶段, 并设置下一阶段的 IR 也为空
            self.IR.pre_EX_MEM.is_empty = True
            return
        else:
            self.IR.pre_EX_MEM.is_empty = False

        mux_alu_input_a = {ALU_Asrc.RA: self.IR.ID_EX.ra, ALU_Asrc.PC: self.IR.ID_EX.pc}
        mux_alu_input_b = {
            ALU_Bsrc.RB: self.IR.ID_EX.rb,
            ALU_Bsrc.IMM: self.IR.ID_EX.imm,
            ALU_Bsrc.NEXT: 4,
        }

        input_a = mux_alu_input_a[self.IR.ID_EX.ctl_sig.ALU_Asrc]
        input_b = mux_alu_input_b[self.IR.ID_EX.ctl_sig.ALU_Bsrc]

        # 这里优先赋值 rb, 因为后面的 bypass 可能会修改 rb 的结果
        self.IR.pre_EX_MEM.rb = self.IR.ID_EX.rb

        input_a, input_b = self.detect_data_hazard(input_a, input_b)
        if self.IR.bubble:
            return

        alu_result = self.ALU.calc(input_a=input_a, input_b=input_b, op=self.IR.ID_EX.ctl_sig.ALUop)
        self.IR.pre_EX_MEM.alu_result = alu_result

        self.detect_control_hazard(input_a, input_b, alu_result, self.IR.ID_EX.Branch)
        if self.IR.bubble:
            return

        self.IR.pre_EX_MEM.rd = self.IR.ID_EX.rd
        self.IR.pre_EX_MEM.MemRead = self.IR.ID_EX.ctl_sig.MemRead
        self.IR.pre_EX_MEM.MemWrite = self.IR.ID_EX.ctl_sig.MemWrite
        self.IR.pre_EX_MEM.MemtoReg = self.IR.ID_EX.ctl_sig.MemtoReg
        self.IR.pre_EX_MEM.MemOp = self.IR.ID_EX.ctl_sig.MemOp
        self.IR.pre_EX_MEM.RegWrite = self.IR.ID_EX.ctl_sig.RegWrite
        self.IR.pre_EX_MEM.PCsrc = self.IR.ID_EX.ctl_sig.PCsrc
        self.IR.pre_EX_MEM.pc = self.IR.ID_EX.pc
        self.IR.pre_EX_MEM.imm = self.IR.ID_EX.imm

    def stage_mem(self):
        """
        MEM-存储器访问.将数据写入存储器或从存储器中读出数据

        """
        if self.IR.EX_MEM.is_empty:
            # EX_MEM 的 IR 为空, 跳过 MEM 阶段, 并设置下一阶段的 IR 也为空
            self.IR.pre_MEM_WB.is_empty = True
            return
        else:
            self.IR.pre_MEM_WB.is_empty = False

        addr = self.IR.EX_MEM.alu_result
        # 先写后读
        self.memory.write(
            addr=addr,
            write_data=self.IR.EX_MEM.rb,
            MemWrite=self.IR.EX_MEM.MemWrite,
            op=self.IR.EX_MEM.MemOp,
        )
        self.IR.pre_MEM_WB.read_data = self.memory.read(
            addr=addr, MemRead=self.IR.EX_MEM.MemRead, op=self.IR.EX_MEM.MemOp
        )
        self.IR.pre_MEM_WB.alu_result = self.IR.EX_MEM.alu_result
        self.IR.pre_MEM_WB.rd = self.IR.EX_MEM.rd
        self.IR.pre_MEM_WB.MemtoReg = self.IR.EX_MEM.MemtoReg
        self.IR.pre_MEM_WB.RegWrite = self.IR.EX_MEM.RegWrite

    def stage_wb(self):
        """
        WB-写回.将指令运算结果存入指定的寄存器
        """
        if self.IR.MEM_WB.is_empty:
            # MEM_WB 的 IR 为空, 跳过 WB 阶段
            return
        mux_mem_inputs = {
            MemtoReg.READ_DATA: self.IR.MEM_WB.read_data,
            MemtoReg.ALU_RESULT: self.IR.MEM_WB.alu_result,
        }
        write_data = mux_mem_inputs[self.IR.MEM_WB.MemtoReg]
        self.registers.write(
            rd=self.IR.MEM_WB.rd, write_data=write_data, RegWrite=self.IR.MEM_WB.RegWrite
        )

    def update_pc(self):
        """
        更新 PC 指针
        """
        if self.IR.bubble:
            # 冒泡暂停一个周期
            return
        if self.IR.ID_EX.is_empty:
            # 1. 流水线初期, 还没有 ID 阶段
            # 2. ID 阶段被跳过时
            self.pc += 4
        else:
            # 对于 ID 阶段解析为 B/J 型指令, 直接判断跳转条件和地址
            if (
                not self.IR.EX_MEM.is_empty
                and self.IR.pre_EX_MEM.PCsrc == PCsrc.IMM
                and self.IR.pre_EX_MEM.branch_cond
            ):
                new_pc = self.ID_adder.calc(self.IR.pre_EX_MEM.pc, self.IR.pre_EX_MEM.imm)
            elif self.IR.pre_ID_EX.is_empty:
                new_pc = self.pc + 4
            elif self.IR.pre_ID_EX.ctl_sig.PCsrc == PCsrc.JALR:
                a = self.IR.pre_ID_EX.ra
                # TODO: test
                new_pc = self.ID_adder.calc(a, self.IR.pre_ID_EX.imm)
                self.IR.pre_IF_ID.is_empty = True
            elif self.IR.pre_ID_EX.ctl_sig.PCsrc == PCsrc.JAL:
                new_pc = self.ID_adder.calc(self.IR.IF_ID.pc, self.IR.pre_ID_EX.imm)
                self.IR.pre_IF_ID.is_empty = True
            elif self.IR.pre_ID_EX.ctl_sig.PCsrc == PCsrc.AUIPC:
                new_pc = self.IR.pre_ID_EX.imm
                self.IR.pre_IF_ID.is_empty = True
            elif self.IR.pre_ID_EX.ctl_sig.PCsrc in (PCsrc.PC, PCsrc.IMM):
                new_pc = self.pc + 4
            else:
                raise ValueError(f"unknown PCsrc {self.IR.pre_ID_EX.ctl_sig.PCsrc}")

            self.pc = new_pc

    def detect_data_hazard(self, input_a, input_b):
        """
        检测数据冒险

        优先检查靠后的 MEM_WB, 其次检查数据更新更靠前的 EX_MEM
        """
        if not self.IR.MEM_WB.is_empty and self.IR.MEM_WB.RegWrite is True:
            # 如果有 MemtoReg 则使用 read_data
            # 否则使用 alu_result
            bypass_data = (
                self.IR.MEM_WB.read_data
                if self.IR.MEM_WB.MemtoReg is MemtoReg.READ_DATA
                else self.IR.MEM_WB.alu_result
            )
            if self.IR.ID_EX.rs1 == self.IR.MEM_WB.rd:
                input_a = bypass_data
            if self.IR.ID_EX.rs2 == self.IR.MEM_WB.rd:
                input_b = bypass_data

        if not self.IR.EX_MEM.is_empty and self.IR.EX_MEM.RegWrite:
            if self.IR.EX_MEM.MemRead and self.IR.EX_MEM.rd in (
                self.IR.ID_EX.rs1,
                self.IR.ID_EX.rs2,
            ):
                # 要读内存到寄存器的 I_LOAD 指令 lb lw
                # 必须空一个周期
                self.IR.bubble = True
            else:
                # 一些要写寄存器的 R 和 I 型指令
                # 直接 bypass 过去
                if self.IR.ID_EX.rs1 == self.IR.EX_MEM.rd:
                    input_a = self.IR.EX_MEM.alu_result
                if self.IR.ID_EX.rs2 == self.IR.EX_MEM.rd:
                    self.IR.pre_EX_MEM.rb = self.IR.EX_MEM.alu_result
                    if self.IR.ID_EX.ctl_sig.ALU_Bsrc == ALU_Bsrc.RB:
                        input_b = self.IR.EX_MEM.alu_result

        return input_a, input_b

    def detect_control_hazard(self, a, b, alu_result, branch_type: BFunct3):
        """
        B 型指令的控制冒险检测

        J 型指令已经在 ID 阶段提前计算
        """
        if branch_type is None:
            self.IR.pre_EX_MEM.branch_cond = False
            return
        # ZF:零标志位(如果结果等于0,则设置为1,否则设置为0)
        zf = 1 if alu_result == 0 else 0
        # SF:符号标志位(如果结果为负数,则设置为1,否则设置为0)
        sf = 1 if alu_result < 0 else 0
        # OF:溢出标志位(如果结果溢出,则设置为1,否则设置为0)
        of = (
            1 if (a > 0 and b < 0 and alu_result < 0) or (a < 0 and b > 0 and alu_result > 0) else 0
        )
        # CF:进位标志位(如果a小于b,则设置为1,否则设置为0)
        cf = 1 if a < b else 0
        if self.check_branch_condition(branch_type, zf, sf, of, cf):
            self.IR.pre_EX_MEM.branch_cond = True
            # 清空 IF_ID ID_EX 的 IR 内容
            self.IR.pre_IF_ID.is_empty = True
            self.IR.pre_ID_EX.is_empty = True
        else:
            self.IR.pre_EX_MEM.branch_cond = False

    def check_branch_condition(self, branch_type: BFunct3, zf, sf, of, cf) -> bool:
        """
        根据四个符号位判断跳转条件
        """
        if branch_type == BFunct3.BEQ:
            return zf == 1
        elif branch_type == BFunct3.BNE:
            return zf == 0
        elif branch_type == BFunct3.BLT:
            return sf ^ of == 1
        elif branch_type == BFunct3.BGE:
            return sf ^ of == 0
        elif branch_type == BFunct3.BLTU:
            return cf == 1
        elif branch_type == BFunct3.BGEU:
            return cf == 0
        else:
            raise ValueError(f"unknown branch type {branch_type}")

    def show_info(self, info=None):
        mem_addr_start = 0
        mem_range = 20
        mem_align = 4
        register_range = 32
        register_align = 8

        if info is not None:
            print(info)
        print("-" * 20)
        for i in range(mem_range // mem_align):
            for j in range(mem_align):
                index = i * mem_align + j
                print(
                    f"mem[{index + mem_addr_start:2}] = {self.memory[index + mem_addr_start]:3}",
                    end=" |",
                )
            print("")
        print("-" * 20)
        for i in range(register_range // register_align):
            for j in range(register_align):
                index = i * register_align + j
                print(f"r{index:<2} = {self.registers[index]:3}", end=" |")
            print("")
        print("-" * 20)

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
