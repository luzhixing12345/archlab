from base import *

class Instruction:
    def __init__(self) -> None:
        print(f'{self.__class__.__name__}')
        self.control_signal = ControlSignal()

    def get_control_signal(self) -> ControlSignal:
        raise NotImplementedError("each instruction should overwrite it to generate control signal")

class R_ADD(Instruction):
    ...

class R_SUB(Instruction):
    ...


class R_SLL(Instruction):
    ...


class R_SLT(Instruction):
    ...


class R_SLTU(Instruction):
    ...


class R_XOR(Instruction):
    
    def get_control_signal(self) -> ControlSignal:
        
        self.control_signal.ALUsrc = ALUsrc.RB
        self.control_signal.ALUop = ALUop.XOR
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = False
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.ALU_RESULT
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class R_SRL(Instruction):
    ...


class R_SRA(Instruction):
    ...


class R_OR(Instruction):
    ...


class R_AND(Instruction):
    ...


class I_ADDI(Instruction):
    ...


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
    ...


class I_LB(Instruction):
    def get_control_signal(self) -> ControlSignal:
        self.control_signal.ALUsrc = ALUsrc.IMM
        self.control_signal.ALUop = ALUop.ADD
        self.control_signal.RegWrite = True
        self.control_signal.MemRead = True
        self.control_signal.MemWrite = False
        self.control_signal.MemtoReg = MemtoReg.READ_DATA
        self.control_signal.PCsrc = PCsrc.PC
        return self.control_signal


class I_LH(Instruction):
    ...


class I_LW(Instruction):
    ...


class I_LBU(Instruction):
    ...


class I_LHU(Instruction):
    ...


class S_SB(Instruction):
    ...


class S_SH(Instruction):
    ...


class S_SW(Instruction):
    ...


class B_BEQ(Instruction):
    ...


class B_BNE(Instruction):
    ...


class B_BLT(Instruction):
    ...


class B_BGE(Instruction):
    ...


class B_BLTU(Instruction):
    ...


class B_BGEU(Instruction):
    ...


class U_LUI(Instruction):
    ...


class U_AUIPC(Instruction):
    ...


class J_JAL(Instruction):
    ...
