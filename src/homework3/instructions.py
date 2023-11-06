from base import *


class Instruction:
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        # print(f"{self.name}")
        self.control_signal = ControlSignal()

    def get_control_signal(self):
        raise NotImplementedError(f"{self.name} should overwrite get_control_signal")


class R_ADD(Instruction):
    def get_control_signal(self):
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.RB
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class R_SUB(Instruction):
    def get_control_signal(self):
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.RB
        self.control_signal.ALUop = ALUop.SUB
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class R_SLL(Instruction):
    ...


class R_SLT(Instruction):
    ...


class R_SLTU(Instruction):
    ...


class R_XOR(Instruction):
    def get_control_signal(self) -> ControlSignal:
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.RB
        self.control_signal.ALUop = ALUop.XOR
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class R_SRL(Instruction):
    ...


class R_SRA(Instruction):
    ...


class R_OR(Instruction):
    def get_control_signal(self):
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.RB
        self.control_signal.ALUop = ALUop.OR
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class R_AND(Instruction):
    def get_control_signal(self):
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.RB
        self.control_signal.ALUop = ALUop.AND
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class I_ADDI(Instruction):
    def get_control_signal(self) -> ControlSignal:
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.IMM
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class I_SLTI(Instruction):
    ...


class I_SLTIU(Instruction):
    ...


class I_XORI(Instruction):
    ...


class I_ORI(Instruction):
    ...


class I_ANDI(Instruction):
    ...


class I_SLLI(Instruction):
    ...


class I_SRLI(Instruction):
    ...


class I_SRAI(Instruction):
    ...


class I_JALR(Instruction):
    
    def get_control_signal(self):
        
        self.control_signal.ALU_Asrc = ALU_Asrc.PC
        self.control_signal.ALU_Bsrc = ALU_Bsrc.NEXT
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.JALR
        return self.control_signal


class I_LB(Instruction):
    def get_control_signal(self) -> ControlSignal:
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.IMM
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = True
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.READ_DATA
        self.control_signal.MemOp = MemOp.SIGN1
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class I_LH(Instruction):
    ...


class I_LW(Instruction):
    def get_control_signal(self) -> ControlSignal:
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.IMM
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = True
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.READ_DATA
        self.control_signal.MemOp = MemOp.SIGN4
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class I_LBU(Instruction):
    ...


class I_LHU(Instruction):
    ...


class S_SB(Instruction):
    def get_control_signal(self) -> ControlSignal:
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.IMM
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = False
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = True
        self.control_signal.MemtoReg = MemtoReg.READ_DATA
        self.control_signal.MemOp = MemOp.SIGN1
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class S_SH(Instruction):
    ...


class S_SW(Instruction):
    def get_control_signal(self) -> ControlSignal:
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.IMM
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = False
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = True
        self.control_signal.MemtoReg = MemtoReg.READ_DATA
        self.control_signal.MemOp = MemOp.SIGN4
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class B_BEQ(Instruction):
    ...


class B_BNE(Instruction):
    def get_control_signal(self):
        # 这里的 ALUsrc 是 RB 而不是 IMM 是因为优化了流水线结构
        # 在 ID 阶段之后添加了 branch_ALU 用于比较计算
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.RB
        self.control_signal.ALUop = ALUop.SUB
        self.control_signal.RegWrite = False
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.READ_DATA
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.IMM
        return self.control_signal


class B_BLT(Instruction):
    ...


class B_BGE(Instruction):
    ...


class B_BLTU(Instruction):
    ...


class B_BGEU(Instruction):
    ...


class U_LUI(Instruction):
    
    def get_control_signal(self):
        self.control_signal.ALU_Asrc = ALU_Asrc.RA
        self.control_signal.ALU_Bsrc = ALU_Bsrc.IMM
        self.control_signal.ALUop = ALUop.OUTPUT_B
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal

class U_AUIPC(Instruction):
    ...


class J_JAL(Instruction):
    def get_control_signal(self):
        self.control_signal.ALU_Asrc = ALU_Asrc.PC
        self.control_signal.ALU_Bsrc = ALU_Bsrc.NEXT
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.MemOp = MemOp.NONE
        self.control_signal.PCsrc = PCsrc.IMM
        return self.control_signal
