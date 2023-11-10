
# pipeline-profiling

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework3.jpg)

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework3.png)

## 运行结果

> jupyter 提交版见 [archlab main.ipynb](https://github.com/luzhixing12345/archlab/blob/main/src/homework3/main.ipynb)

本实验结果分为两部分, 首先是对于 5 级流水线功能实现的检验

```bash
python src/homework3/test.py
```

运行通过所有测试案例, 其中所有测试的的源汇编代码保存在 `asmcode/`, test.py 中每一个测试案例对应相应的汇编代码

> 这一部分会在后文解释

```bash
Pass test_CTL1
.Pass test_CTL2
.Pass test_DH1
.Pass test_DH2
.Pass test_DH3
.Pass test_DH_RAW
.Pass test_DH_WAR
.Pass test_DH_WAW
.
----------------------------------------------------------------------
Ran 7 tests in 0.012s

OK
```

然后是对于本次指令重排加速的实现和测试

```bash
python src/homework3/main.py
```

```txt
   basic step = 7008
schedule step = 6003
   improvment = 7008-6003/7008 = 14.34%
```

其中原指令序列执行共 7008 步, 重排后的指令执行 6003 步, 优化提升了 14% 的效率

## 实验报告

### 实验分析

考虑到已经开始涉及到指令调度和重排, 而传统的单周期 ISA 已经不再适合(因为单周期没有重排指令的必要), 因此本次实验需要完成一个五级流水线的 ISA 

正常来说 5 阶段 IF ID EX MEM WB 在流水线是同步执行的, 通用寄存器组和存储器在时钟上升沿写入, 中间寄存器(下文简称IR)在时钟下降沿写入

下图是一个简化版的五级流水阶段示意图, 核心问题的是 **如何实现在前一阶段将新数据写入 IR 之前后一阶段已经从 IR 把旧数据读取出来, 例如在 IF 写入 IF_ID 之前, ID 已经读取到了 IF_ID 中的值**

![20231108181447](https://raw.githubusercontent.com/learner-lu/picbed/master/20231108181447.png)

考虑到 Python 没有办法像 Verilog 一样做到电路信号级模拟, 理论上来说如果想要实现时序级模拟, 需要使用 5 个线程和 5 把锁, 将 IR 作为资源临界区来获取和释放锁, 以保证并发的线程读取 IR 和写入 IR 不发生顺序上的冲突

但实际上依然可以使用串行的方式, **采用双倍的 IR 将读和写分开, 并更新 IR**

1. 每一个流水线阶段都从前一个 IR 中读, 写入到后一个 IR(下文和代码中称为 pre_IR);
2. 每一个流水线阶段的 IR 使用 pre_IR 的内容替换 IR 的内容

![20231108183636](https://raw.githubusercontent.com/learner-lu/picbed/master/20231108183636.png)

![20231108183901](https://raw.githubusercontent.com/learner-lu/picbed/master/20231108183901.png)

相当于采用了双倍的硬件资源, 在所有阶段完成之后同步更新 IR 的值, 这样就实现了串行的读写分离, 笔者选择采用这种方式来模拟流水线执行

### 代码实现

> 说实话代码实现的文档不是很好写, 因为实际上更多的是作者在工程实践上的选择, 一下子抛给读者一个完整的 ISA 实现, 很大概率会直接陷入代码细节之中, 因此笔者打算一步一步的按执行流程来解释代码实现, 并在对应位置给出该模块的设计思路.

开始之前先总览一下目录结构, 本次代码位于 `src/homework3`

```bash
.
├── asm
│   ├── Makefile
│   ├── loop.S              # 汇编代码
│   ├── loop.c              # C 代码
│   └── schedule_loop.S     # 汇编的重排序
├── base.py                 # 基础枚举类型和类定义
├── instructions.py         # RISCV 32I 指令集
├── isa.py                  # Pipeline ISA
├── main.ipynb
├── main.py                 # 主函数入口
├── test.py                 # Pipeline ISA 正确性测试文件
└── testcase                # 测试用例
    ├── CTL1.S
    ├── DH1.S
    ├── DH2.S
    ├── DH3.S
    ├── DH_RAW.S
    ├── DH_WAR.S
    └── DH_WAW.S
```

其中 testcase 为一些测试用例, test.py 中为这些测试用例对应的使用. `asm/loop.c` 为题目中测试代码的 C 函数表示

```c
void loop_test(int *x, int s) {
    for (int i = 999; i >= 0; i--) {
        x[i] = x[i] + s;
    }
}
```

可以使用如下命令查看反汇编结果

```bash
riscv64-linux-gnu-gcc -march=rv32i -mabi=ilp32 -Ofast -c loop.c -o example.o
riscv64-linux-gnu-objdump example.o -d
```

```riscvasm
00000000 <loop_test>:
   0:   000017b7                lui     a5,0x1          # a5 = 1<<12 = 4096
   4:   f9c78793                addi    a5,a5,-100      # a5 = 3096 ( = 999 x 4)
   8:   00f507b3                add     a5,a0,a5        # a5 = x + 3096 (x[999])

0000000c <.L2>:
   c:   0007a703                lw      a4,0(a5)        # a4 = x[i]
  10:   00078693                mv      a3,a5           # a3 = &x
  14:   ffc78793                addi    a5,a5,-4        # x--
  18:   00b70733                add     a4,a4,a1        # a4 += s
  1c:   00e7a223                sw      a4,4(a5)        # x[i] = a4
  20:   fed516e3                bne     a0,a3,c <.L2>
  24:   00008067                ret
```

除此之外对于浮点数的计算有如下假设, 下图中的延迟表示**如果后续的指令(FP ALU op/Store double)使用到了前面指令(FP ALU op/Load double)的结果, 那么需要额外添加 x 个延迟周期**

![20231109105011](https://raw.githubusercontent.com/learner-lu/picbed/master/20231109105011.png)

因此对于原循环来说, 一个修改后的结果 loop.S 如下:

```riscvasm
    lui     a5,0x1
    addi    a5,a5,-100
    add     a5,a0,a5
L2:
    lw      a4,0(a5)
    nop
    add     a4,a4,a1
    nop
    nop
    sw      a4,4(a5)
    addi    a5,a5,-4
    nop
    bne     a0,a5, L2
    ret
```

重排后的指令 schedule_loop.S 如下:

```riscvasm
    lui     a5,0x1
    addi    a5,a5,-100
    add     a5,a0,a5
L2:
    lw      a4,0(a5)
    addi    a5,a5,-4
    add     a4,a4,a1
    nop
    bne     a0,a5, L2
    sw      a4,4(a5)
    ret
```

至此就可以利用工具得到这两段汇编代码所对应的机器码, 然后对比这两段代码运行的 step 即可, 这也就是 main.py 所做的事

> 其中设置 register[10] 和 [11] 相当于设置 a0 和 a1, 即 x 数组地址为 0x200, s 的值为 1

```python
def main():

    # basic loop -> loop.S
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

    isa = PipelineISA()
    isa.registers[10] = 0x200
    isa.registers[11] = 1
    isa.load_instructions(instructions)
    isa.run()
    basic_step = isa.step

    # schedule loop -> schedule_loop.S
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
```

---

#### 流水线设计

开始之前先来简单回顾一下经典五阶段流水线的内容

## 参考

- [RISC-V控制单元的简单介绍](https://zhuanlan.zhihu.com/p/471466242)
- [RISCV32I CPU](https://nju-projectn.github.io/dlco-lecture-note/exp/11.html)
- [基于RISC-V架构-五级流水线CPU](https://zhuanlan.zhihu.com/p/453232311)
- [基于RISC-V的CPU设计入门__控制冒险](https://www.sunnychen.top/archives/rvintroch)