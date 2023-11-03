from instructions import *
from isa import *


class Riscv32(PipelineISA):
    """
    RISCV 32I 五级流水线
    """

    def stage_id(self):
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

        self.IR.pre_ID_EX.rs1 = instruction_info.rs1
        self.IR.pre_ID_EX.rs2 = instruction_info.rs2
        self.IR.pre_ID_EX.ra, self.IR.pre_ID_EX.rb = self.registers.read(
            instruction_info.rs1, instruction_info.rs2
        )
        self.IR.pre_ID_EX.rd = instruction_info.rd
        self.IR.pre_ID_EX.imm = instruction_info.imm
        self.IR.pre_ID_EX.ctl_sig = self.get_control_signal(instruction_info)

    def get_control_signal(self, instruction_info: InstructionInfo) -> ControlSignal:
        """ """
        


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
    #     lb a5, 1(a0)
    #     lb a6, 1(a0)
    #     lb a7, 1(a0)
    # L2:
    #     sb a2, 3(a0)

    # 编译为 32 位 RISCV 目标文件

    # riscv64-linux-gnu-gcc -march=rv32i -mabi=ilp32 -c example.S -o example.o
    # riscv64-linux-gnu-objdump example.o -d

    instructions = [
        0x00A54533,
        0x00050583,
        0x00150603,
        0x00158593,
        0x00360613,
        0xFEC59CE3,
        0x0100076F,
        0x00150783,
        0x00150803,
        0x00150883,
        0x00C501A3,
    ]

    isa = Riscv32()
    isa.load_instructions(instructions)
    isa.run()
    isa.show_info("after")


if __name__ == "__main__":
    main()
