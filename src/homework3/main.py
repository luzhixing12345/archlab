from instructions import *
from isa import *


def main():

    # basic loop
    instructions = [
        0x000017B7,
        0xF9C78793,
        0x00F507B3,
        0x0007A703,
        0x00078693,
        0xFFC78793,
        0x00B70733,
        0x00E7A223,
        0xFED516E3,
        0x00008067,
    ]

    # schedule loop
    schedule_instructions = [
        0x000017B7,
        0xF9C78793,
        0x00F507B3,
        0x0007A703,
        0xFFC78793,
        0x00B70733,
        0x00000013,
        0xFEF518E3,
        0x00E7A223,
        0x00008067,
    ]

    isa = PipelineISA()
    isa.registers[10] = 0x200
    isa.registers[11] = 1
    isa.load_instructions(instructions)
    isa.run()
    basic_step = isa.step
    
    isa.reset()
    isa.registers[10] = 0x200
    isa.registers[11] = 1
    isa.load_instructions(schedule_instructions)
    isa.run()
    schedule_step = isa.step

    print(f"   basic step = {basic_step}")
    print(f"schedule step = {schedule_step}")
    print(f"   improvment = {basic_step}-{schedule_step}/{basic_step} = {(basic_step-schedule_step)/basic_step * 100:.2f}%")

if __name__ == "__main__":
    main()
