
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

本次代码位于 `src/homework3`, 文件结构如下

```bash
.
├── asmcode             # 测试用例
│   ├── CTL1.S
│   ├── DH1.S
│   ├── DH2.S
│   ├── DH3.S
│   ├── DH_RAW.S
│   ├── DH_WAR.S
│   └── DH_WAW.S
├── base.py             # 基础枚举类型和类定义
├── instructions.py     # RISCV 32I 指令集
├── isa.py              # Pipeline ISA
├── loop.S              # 汇编代码
├── loop.c              # C 代码
├── main.py             # 主函数入口
├── schedule_loop.S     # 汇编的重排序
└── test.py             # Pipeline ISA 正确性测试文件
```

其中 asmcode 为一些测试用例, test.py 中为这些测试用例对应的使用. `loop.c` 为题目中测试代码的 C 函数表示

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
   0:   000017b7                lui     a5,0x1
   4:   f9c78793                addi    a5,a5,-100 # f9c <.L2+0xf90>
   8:   00f507b3                add     a5,a0,a5

0000000c <.L2>:
   c:   0007a703                lw      a4,0(a5)
  10:   00078693                mv      a3,a5
  14:   ffc78793                addi    a5,a5,-4
  18:   00b70733                add     a4,a4,a1
  1c:   00e7a223                sw      a4,4(a5)
  20:   fed516e3                bne     a0,a3,c <.L2>
  24:   00008067                ret
```



## 参考

- [RISC-V控制单元的简单介绍](https://zhuanlan.zhihu.com/p/471466242)
- [RISCV32I CPU](https://nju-projectn.github.io/dlco-lecture-note/exp/11.html)
- [基于RISC-V架构-五级流水线CPU](https://zhuanlan.zhihu.com/p/453232311)
- [基于RISC-V的CPU设计入门__控制冒险](https://www.sunnychen.top/archives/rvintroch)