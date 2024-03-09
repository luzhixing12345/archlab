from typing import List, Optional
from enum import Enum
import re

KB = 1024

class Status(Enum):
    MODIFIED = "M"
    EXCLUSIVE = "E"
    SHARE = "S"
    INVALID = "I"


class Operator(Enum):
    READ = "read"
    WRITE = "write"


class Instruction:
    def __init__(self, p_id: int, op: Operator, address: int, value: Optional[int]) -> None:
        self.p_id = p_id
        self.op = op
        self.address = address
        self.value = value


class CacheLine:

    def __init__(self, block_size: int = 32) -> None:
        self.block_size = block_size


class Cache:

    def __init__(self, cache_size: int = 32 * KB) -> None:
        self.cache_size = cache_size


class Processor:

    def __init__(self, p_id: int) -> None:
        self.p_id = p_id
        self.status = Status.INVALID


class CacheCoherence:
    """
    MESI
    """

    def __init__(self) -> None:
        cpu_number = 4
        self.cpus = [Processor(i) for i in range(cpu_number)]

    def run_test_case(self, filename: str) -> None:

        print("-" * 40)
        print(f"running test case {filename}\n")

        instructions = self.parse_test_case(filename)

    def parse_test_case(self, filename: str) -> List[Instruction]:
        """
        <Pn, op, addr, value>
        """
        pattern = re.compile(r"<P(\d*), *(\w*), *(\d*), *(-|[0-9]*) *>")
        instructions: List[Instruction] = []
        with open(filename, "r") as f:
            instruction_strs = f.read().split("\n")
            for instruction_str in instruction_strs:
                match_group = pattern.match(instruction_str)
                if match_group:
                    p_id = int(match_group.group(1))
                    op = Operator(match_group.group(2))
                    address = int(match_group.group(3))
                    if op == Operator.WRITE:
                        value = int(match_group.group(4))
                    else:
                        value = None
                    instructions.append(Instruction(p_id, op, address, value))

        return instructions


def main():

    test_case_filenames = ["Normal.txt", "random.txt", "false sharing.txt"]
    cache_coherence = CacheCoherence()
    for filename in test_case_filenames:
        cache_coherence.run_test_case(filename)


if __name__ == "__main__":
    main()
