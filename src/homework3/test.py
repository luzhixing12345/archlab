from isa import *
import unittest

class MyTestCase(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.isa = PipelineISA()

    def test_DH1(self):
        instructions = [
            0x003100B3,
            0x40308233,
            0x0070F333,
            0x0090E433,
            0x00B0C533,
        ]
        self.isa.reset()
        self.isa.registers[2] = 1
        self.isa.registers[3] = 2
        self.isa.registers[7] = 10
        self.isa.registers[9] = 4
        self.isa.registers[11] = 3
        self.isa.load_instructions(instructions)
        self.isa.run()

        self.assertEqual(self.isa.registers[1], 3)
        self.assertEqual(self.isa.registers[4], 1)
        self.assertEqual(self.isa.registers[6], 2)
        self.assertEqual(self.isa.registers[8], 7)
        self.assertEqual(self.isa.registers[9], 4)
        self.assertEqual(self.isa.registers[10], 0)
        print(f"\033[92mPass test_DH1\033[0m")

    def test_DH2(self):
        instructions = [
            0x00000103,
            0x003100B3,
            0x40308233,
            0x0070F333,
            0x0090E433,
            0x00B0C533,
        ]
        self.isa.reset()
        self.isa.memory[0] = 1
        self.isa.registers[3] = 2
        self.isa.registers[7] = 10
        self.isa.registers[9] = 4
        self.isa.registers[11] = 3

        self.isa.load_instructions(instructions)
        self.isa.run()

        self.assertEqual(self.isa.registers[1], 3)
        self.assertEqual(self.isa.registers[4], 1)
        self.assertEqual(self.isa.registers[6], 2)
        self.assertEqual(self.isa.registers[8], 7)
        self.assertEqual(self.isa.registers[9], 4)
        self.assertEqual(self.isa.registers[10], 0)
        print(f"\033[92mPass test_DH2\033[0m")

    def test_DH3(self):
        instructions = [
            0x00004033,
            0x00000083,
            0x00100103,
            0x00110113,
            0x002001A3,
            0x00108193,
            0x00310233,
            0x004002A3,
        ]
        self.isa.reset()
        self.isa.memory[0] = 100
        self.isa.memory[1] = 200

        self.isa.load_instructions(instructions)
        self.isa.run()

        self.assertEqual(self.isa.registers[1], 100)
        self.assertEqual(self.isa.registers[2], 201)
        self.assertEqual(self.isa.registers[3], 101)
        self.assertEqual(self.isa.registers[4], 302)
        self.assertEqual(self.isa.memory[3], 201)
        self.assertEqual(self.isa.memory[5], 302)
        print(f"\033[92mPass test_DH3\033[0m")

    def test_DH_WAW(self):
        instructions = [
            0x403100B3,
            0x003100B3,
        ]
        self.isa.reset()
        self.isa.registers[2] = 100
        self.isa.registers[3] = 1

        self.isa.load_instructions(instructions)
        self.isa.run()

        self.assertEqual(self.isa.registers[1], 101)
        print(f"\033[92mPass test_DH_WAW\033[0m")

    def test_DH_WAR(self):
        instructions = [
            0x003100B3,
            0x40308233,
        ]
        self.isa.reset()
        self.isa.registers[2] = 100
        self.isa.registers[3] = 1

        self.isa.load_instructions(instructions)
        self.isa.run()

        self.assertEqual(self.isa.registers[1], 101)
        self.assertEqual(self.isa.registers[4], 100)
        print(f"\033[92mPass test_DH_WAR\033[0m")

    def test_DH_RAW(self):
        instructions = [
            0x40308233,
            0x003100B3,
        ]
        self.isa.reset()
        self.isa.registers[1] = 10
        self.isa.registers[2] = 100
        self.isa.registers[3] = 1

        self.isa.load_instructions(instructions)
        self.isa.run()

        self.assertEqual(self.isa.registers[1], 101)
        self.assertEqual(self.isa.registers[4], 9)
        print(f"\033[92mPass test_DH_RAW\033[0m")

    def test_CTL1(self):
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
        self.isa.reset()
        self.isa.memory[0] = 20
        self.isa.memory[1] = 0

        self.isa.load_instructions(instructions)
        self.isa.run()

        self.assertEqual(self.isa.memory[3], 30)
        self.assertEqual(self.isa.registers[11], 30)
        self.assertEqual(self.isa.registers[12], 30)
        self.assertEqual(self.isa.registers[14], 284)
        print(f"\033[92mPass test_CTL1\033[0m")


if __name__ == "__main__":
    unittest.main()
