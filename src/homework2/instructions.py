# RISCV 32I 指令集介绍可以参考
# https://www.sunnychen.top/archives/riscvbasic
from isa import Instruction


class R_ADD(Instruction):
    def stage_ex(self):
        self.isa.IR.value = self.isa.IR.rs1 + self.isa.IR.rs2

    def stage_wb(self):
        self.isa.registers[self.isa.instruction_info.rd] = self.isa.IR.value
        return super().stage_wb()


class R_SUB(Instruction):
    ...


class R_SLL(Instruction):
    ...


class R_SLT(Instruction):
    ...


class R_SLTU(Instruction):
    ...


class R_XOR(Instruction):
    def stage_ex(self):
        self.isa.IR.value = self.isa.IR.rs1 ^ self.isa.IR.rs2

    def stage_wb(self):
        self.isa.registers[self.isa.instruction_info.rd] = self.isa.IR.value
        return super().stage_wb()


class R_SRL(Instruction):
    ...


class R_SRA(Instruction):
    ...


class R_OR(Instruction):
    ...


class R_AND(Instruction):
    ...


class I_ADDI(Instruction):
    def stage_ex(self):
        self.isa.IR.value = self.isa.IR.rs1 + self.isa.instruction_info.imm

    def stage_wb(self):
        self.isa.registers[self.isa.instruction_info.rd] = self.isa.IR.value
        return super().stage_wb()


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
    def stage_ex(self):
        self.isa.IR.value = self.isa.IR.rs1 + self.isa.instruction_info.imm

    def stage_mem(self):
        self.isa.IR.mem_value = self.isa.memory[self.isa.IR.value]

    def stage_wb(self):
        self.isa.registers[self.isa.instruction_info.rd] = self.isa.IR.mem_value
        return super().stage_wb()


class I_LH(Instruction):
    ...


class I_LW(Instruction):
    ...


class I_LBU(Instruction):
    ...


class I_LHU(Instruction):
    ...


class S_SB(Instruction):
    def stage_ex(self):
        self.isa.IR.value = self.isa.IR.rs1 + self.isa.instruction_info.imm

    def stage_mem(self):
        self.isa.memory[self.isa.IR.value] = self.isa.IR.rs2 & 0xFF


class S_SH(Instruction):
    ...


class S_SW(Instruction):
    ...


class B_BEQ(Instruction):
    ...


class B_BNE(Instruction):
    def stage_ex(self):
        if self.isa.IR.rs1 != self.isa.IR.rs2:
            self.isa.pc = self.isa.pc + self.isa.instruction_info.imm
            self.pc_inc = False


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
    def stage_ex(self):
        self.isa.pc += self.isa.instruction_info.imm
        self.pc_inc = False
