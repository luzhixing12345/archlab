from instructions import *
from isa import *


class RISCV32(ISA):
    """
    RISCV 32I 单周期五阶段
    """

    def stage_id(self):
        opcode = self.instruction[-7:]
        opcode_type = OpCode(opcode)
        self.instruction_info.opcode = opcode_type
        if opcode_type == OpCode.R:
            self.instruction_info.funct7 = RFunct7(self.instruction[:7])
            self.instruction_info.rs2 = int(self.instruction[7:12], 2)
            self.instruction_info.rs1 = int(self.instruction[12:17], 2)
            self.instruction_info.funct3 = RFunct3(self.instruction[17:20])
            self.instruction_info.rd = int(self.instruction[20:25], 2)
            self.instruction_info.imm = None
        elif opcode_type in (OpCode.I_LOAD, OpCode.I_CALC, OpCode.I_JALR):
            self.instruction_info.funct7 = None
            self.instruction_info.rs2 = None
            self.instruction_info.rs1 = int(self.instruction[12:17], 2)
            self.instruction_info.funct3 = IFunct3(self.instruction[17:20])
            self.instruction_info.rd = int(self.instruction[20:25], 2)
            self.instruction_info.imm = self.binary_str(self.instruction[:12])
        elif opcode_type == OpCode.S:
            self.instruction_info.funct7 = None
            self.instruction_info.rs2 = int(self.instruction[7:12], 2)
            self.instruction_info.rs1 = int(self.instruction[12:17], 2)
            self.instruction_info.funct3 = SFunct3(self.instruction[17:20])
            self.instruction_info.rd = None
            self.instruction_info.imm = self.binary_str(self.instruction[:7] + self.instruction[20:25])
        elif opcode_type == OpCode.B:
            self.instruction_info.funct7 = None
            self.instruction_info.rs2 = int(self.instruction[7:12], 2)
            self.instruction_info.rs1 = int(self.instruction[12:17], 2)
            self.instruction_info.funct3 = BFunct3(self.instruction[17:20])
            self.instruction_info.rd = None
            self.instruction_info.imm = self.binary_str(
                self.instruction[0]
                + self.instruction[24]
                + self.instruction[1:6]
                + self.instruction[20:24]
                + "0"
            )

        elif opcode_type in (OpCode.U_AUIPC, OpCode.U_LUI):
            self.instruction_info.funct7 = None
            self.instruction_info.rs2 = None
            self.instruction_info.rs1 = None
            self.instruction_info.funct3 = None
            self.instruction_info.rd = int(self.instruction[20:25], 2)
            self.instruction_info.imm = self.binary_str(self.instruction[:20] + "0" * 12)
        elif opcode_type == OpCode.J:
            self.instruction_info.funct7 = None
            self.instruction_info.rs2 = None
            self.instruction_info.rs1 = None
            self.instruction_info.funct3 = None
            self.instruction_info.rd = int(self.instruction[20:25], 2)
            self.instruction_info.imm = self.binary_str(
                self.instruction[0]
                + self.instruction[11:18]
                + self.instruction[10]
                + self.instruction[1:11]
                + "0"
            )
        else:
            raise ValueError("unknown opcode type")

        # 如果指令中包含 rs1 rs2, 则读取对应寄存器的值
        if self.instruction_info.rs1 is not None:
            self.pipeline_register.rs1 = self.registers[self.instruction_info.rs1]

        if self.instruction_info.rs2 is not None:
            self.pipeline_register.rs2 = self.registers[self.instruction_info.rs2]

        self.match_instruction()

    def match_instruction(self):
        """
        通过 ISA 在 ID 阶段解析指令得到的信息, 定位找到具体的指令
        """
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
                IFunct3.ADDI: I_ADDI,
                IFunct3.SLTI: I_SLTI,
                IFunct3.SLTIU: I_SLTIU,
                IFunct3.XORI: I_XORI,
                IFunct3.ORI: I_ORI,
                IFunct3.ANDI: I_ANDI,
                IFunct3.SLLI: I_SLLI,
                IFunct3.SRLI: I_SRLI,
                IFunct3.SRAI: I_SRAI,
            },
            OpCode.I_JALR: {IFunct3.JALR: I_JALR},
            OpCode.I_LOAD: {
                IFunct3.LB: I_LB,
                IFunct3.LH: I_LH,
                IFunct3.LW: I_LW,
                IFunct3.LBU: I_LBU,
                IFunct3.LHU: I_LHU,
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

        if (
            self.instruction_info.funct3 == RFunct3.SUB
            and self.instruction_info.funct7 == RFunct7.SUB
        ):
            self.instruction = R_SUB(self)
        elif (
            self.instruction_info.funct3 == RFunct3.SRA
            and self.instruction_info.funct7 == RFunct7.SRA
        ):
            self.instruction = R_SRA(self)
        elif self.instruction_info.opcode == OpCode.U_AUIPC:
            self.instruction = U_AUIPC(self)
        elif self.instruction_info.opcode == OpCode.U_LUI:
            self.instruction = U_LUI(self)
        elif self.instruction_info.opcode == OpCode.J:
            self.instruction = J_JAL(self)
        else:
            self.instruction = RISCV_32I_instructions[self.instruction_info.opcode][
                self.instruction_info.funct3
            ](self)


def main():
    # 汇编代码见 example.S

    #     xor a0, a0, a0
    #     lb a1, 0(a0)
    #     lb a2, 1(a0)
    # L1:
    #     addi a1, a1, 1
    #     addi a2, a2, 3
    #     bne a1, a2, L1
    #     jal a4, L2
    # L2:
    #     sb a2, 3(a0)

    # 编译为 32 位 RISCV 目标文件

    # riscv64-linux-gnu-gcc -march=rv32i -mabi=ilp32 -c example.S -o example.o
    # riscv64-linux-gnu-objdump example.o -d

    instructions = [
        0x00A54533,
        0x00050583,
        0x00150603,
        0x00360613,
        0x00158593,
        0xFEC59CE3,
        0x0040076F,
        0x00C501A3,
    ]

    isa = RISCV32()
    isa.memory[0] = 20
    isa.memory[1] = 0
    isa.show_info("before")

    isa.load_instructions(instructions)
    isa.run()
    isa.show_info("after")


if __name__ == "__main__":
    main()
