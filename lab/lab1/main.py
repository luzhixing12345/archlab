from typing import List, Optional, Dict
from enum import Enum
import math
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


class BusReqOp(Enum):
    READ_MISS = "read-miss"
    WRITE_MISS = "write-miss"
    INVALID = "invalid"
    WRITE_BACK = "write-back"


class BusReq:

    def __init__(self, p_id: int, op: BusReqOp, address: int) -> None:
        self.p_id = p_id
        self.op = op
        self.address = address


class Instruction:
    def __init__(self, p_id: int, op: Operator, address: int, value: Optional[int]) -> None:
        self.p_id = p_id
        self.op = op
        self.addr = address
        self.value = value

    def __repr__(self) -> str:
        return f"<P{self.p_id} {self.op.value:<5} {self.addr:<4} {'-' if self.value is None else self.value}>"


class CacheLine:

    def __init__(self, block_size: int = 32) -> None:
        self.block_size = block_size
        self.block_values = [None] * self.block_size
        # 正常来说应该使用三个标志位 valid, dirty, share, 但是这里为了简便直接使用一个标志位用于表示状态
        self.status = Status.INVALID
        self.tag = -1

    def read(self, address: int) -> Optional[int]:
        return

    def write(self, address: int, value: int) -> None:
        """ """


class Cache:
    """
    +-----------------------+---------------------+--------------+
    |          tag          |      set index      | block offset |
    +-----------------------+---------------------+--------------+
                13                     10                 5
    """

    def __init__(self, cache_size: int = 32 * KB, block_size: int = 32) -> None:
        """
        默认缓存大小为32KB
        默认块大小为32B
        地址长度为48

        共有 1024 个缓存行
        """
        self.cache_size = cache_size
        self.block_size = block_size

        self.block_index = int(math.log2(block_size))
        self.set_size = cache_size // block_size
        self.cachelines = [CacheLine(block_size) for _ in range(self.set_size)]
        self.set_index = int(math.log2(self.set_size))

        self.addr_len = 48
        self.tag_len = self.addr_len - self.block_index - self.set_index

    def split_addr(self, address: int):
        set_index = (address >> self.block_index) % self.set_size
        block_offset = address & ((1 << self.block_index) - 1)
        tag = address >> (self.block_index + self.set_index)
        print(f"tag: {tag}, set_index: {set_index}, block_offset: {block_offset}")
        return tag, set_index, block_offset

    def read(self, address: int) -> Optional[int]:
        tag, set_index, block_offset = self.split_addr(address)
        cacheline = self.cachelines[set_index]
        if cacheline.f_invalid is True:
            if tag == cacheline.tag:
                return cacheline.read(block_offset)

    def write(self, address: int, value: int) -> None:
        tag, set_index, block_offset = self.split_addr(address)


class Processor:

    def __init__(self, p_id: int, cc_bus: "CacheCoherenceBus") -> None:
        self.p_id = p_id
        self.cache = Cache()
        self.cc_bus = cc_bus

    def error(self, msg: str, instruction: Instruction):
        raise ValueError(f"{msg} in processor {self.p_id}[{cacheline.status}] at address {instruction.addr}")

    def run(self, instruction: Instruction) -> Optional[BusReq]:
        """
        CPU request
        """
        assert instruction.p_id == self.p_id
        tag, set_index, block_offset = self.cache.split_addr(instruction.addr)
        cacheline = self.cache.cachelines[set_index]

        if tag != cacheline.tag:
            # tag miss, write back
            self.cc_bus.memory[instruction.addr] = cacheline.block_values[block_offset]

        if cacheline.status == Status.INVALID:
            if instruction.op == Operator.READ:
                cacheline.status = Status.EXCLUSIVE
                return BusReq(self.p_id, BusReqOp.READ_MISS, instruction.addr)
            elif instruction.op == Operator.WRITE:
                cacheline.status = Status.MODIFIED
                return BusReq(self.p_id, BusReqOp.WRITE_MISS, instruction.addr)
            else:
                raise TypeError(f"invalid operation: {instruction.op}")
        elif cacheline.status == Status.EXCLUSIVE:
            if instruction.op == Operator.READ:
                if self.cache.read(instruction.addr) is not None:
                    # read hit, no bus request
                    pass
                else:
                    self.error("read miss", instruction)
            elif instruction.op == Operator.WRITE:
                if self.cache.write(instruction.addr, instruction.value) is not None:
                    # write hit
                    cacheline.status = Status.MODIFIED
                    # no bus request in MESI
                else:
                    self.error("write miss", instruction)
            else:
                raise TypeError(f"invalid operation: {instruction.op}")
        elif cacheline.status == Status.MODIFIED:
            if instruction.op == Operator.READ:
                if self.cache.read(instruction.addr) is not None:
                    # read hit, no bus request
                    pass
                else:
                    self.error("read miss", instruction)
            elif instruction.op == Operator.WRITE:
                if self.cache.write(instruction.addr, instruction.value) is not None:
                    # write hit, no bus request
                    pass
                else:
                    self.error("write miss", instruction)
            else:
                raise TypeError(f"invalid operation: {instruction.op}")
        elif cacheline.status == Status.SHARE:
            if instruction.op == Operator.READ:
                if self.cache.read(instruction.addr) is not None:
                    # read hit, no bus request
                    pass
                else:
                    self.error("read miss", instruction)
            elif instruction.op == Operator.WRITE:
                if self.cache.write(instruction.addr, instruction.value) is not None:
                    # write hit
                    cacheline.status = Status.MODIFIED
                    return BusReq(self.p_id, BusReqOp.INVALID, instruction.addr)
                else:
                    self.error("write miss", instruction)
            else:
                raise TypeError(f"invalid operation: {instruction.op}")

        else:
            raise ValueError(f"invalid status: {cacheline.status}")
        return None

    def snope(self, bus_req: BusReq) -> None:
        """
        Bus request
        """

    def __repr__(self) -> str:

        return f"[P{self.p_id}]"

class Memory:
    
    def __init__(self) -> None:
        self.memory = {}
    
    def __getitem__(self, address: int):
        if address not in self.memory:
            self.memory[address] = 0
        return self.memory[address]
    
    def __setitem__(self, address: int, value: int):
        self.memory[address] = value

class CacheCoherenceBus:
    """
    MESI snope
    """

    def __init__(self) -> None:
        cpu_number = 4
        self.cpus = [Processor(i, self) for i in range(cpu_number)]
        self.memory = Memory()

    def run_test_case(self, filename: str) -> None:

        print("-" * 40)
        print(f"running test case {filename}\n")

        instructions = self.parse_test_case(filename)
        for instruction in instructions:
            bus_req = self.cpus[instruction.p_id].run(instruction)
            # 将 bus_req 传递给其他 cpu
            if bus_req is not None:
                for i in range(len(self.cpus)):
                    if i != instruction.p_id:
                        self.cpus[i].snope(bus_req)

        for cpu in self.cpus:
            print(cpu)

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
                else:
                    raise ValueError(f"invalid instruction: {instruction_str}")

        return instructions


def main():

    test_case_filenames = ["Normal.txt", "random.txt", "false sharing.txt"]
    cc_bus = CacheCoherenceBus()
    for filename in test_case_filenames:
        cc_bus.run_test_case(filename)


if __name__ == "__main__":
    main()
