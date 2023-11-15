
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
   basic step = 8007
schedule step = 7001
   improvment = 8007-7001/8007 = 12.56%
```

其中原指令序列执行共 8007 步, 重排后的指令执行 7001 步, 优化提升了 12.56% 的效率

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

### 流水线设计

这一部分我们重新回顾一下流水线的设计

> 下文讨论的内容为 RISCV 32I 指令集在标准五级流水线上的情况

标准的五级流水线分为 `IF ID EX MEM WB` 五个阶段, 每两个阶段之间有一个中间寄存器 IR, 分别为 `IF_ID ID_EX EX_MEM MEM_WB`

下图是各个阶段的简化内容:

- `IF`: 根据 PC 寄存器的值读取一条指令(instruction), 存入 IF_ID 中
- `ID`: 从 IF_ID 中取出指令, 根据 RISCV 指令设计规则拿到相关信息, 读取 rs1 rs2 寄存器的值, 将结果(ra rb)同其他信息(others)一同写入 ID_EX
- `EX`: 从 ID_EX 中取出信息, 并将两个值送入 ALU 中进行计算, 拿到计算结果(result), 同其他信息(others)一同写入 EX_MEM
- `MEM`: 从 EX_MEM 中取出信息, 将 write_data 的值写入 address 或者从 address 读取 read_data, 同其他信息(others)一同写入 MEM_WB
- `WB`: 从 MEM_WB 中取出信息, 将 write_data 写入 rd

![20231113213334](https://raw.githubusercontent.com/learner-lu/picbed/master/20231113213334.png)

相信读者可以注意到笔者在表述的过程中频繁使用到了 "**其他信息(others)**" 这样一个词语. 同时上述文字存在一些模糊不清的说法, 比如 EX 阶段的 "**将两个值**(什么值)" "**进行计算**(进行什么计算)", MEM 阶段的 "**写入或者读取**(怎么判断读还是写, 怎么写入, 怎么读取)", WB 阶段的 "**write_data 写入 rd**(其实不一定写入)", 以及一个很重要的问题: "**PC 如何更新**"

为了回答上面的问题首先需要介绍一下**控制信号**. RISCV 在确定指令类型(opcode)后,**需要生成每个指令对应的控制信号,来控制数据通路部件进行对应的动作**.控制信号生产部件(Control Signal Generator)是根据instr中的操作码 `opcode` ,及 `func3` 和 `func7` 来生成对应的控制信号的, 主要有如下的几个控制信号

- `ALU_Asrc`: ALU 的第一个输入选择哪一个
- `ALU_Bsrc`: ALU 的第二个输入选择哪一个
- `ALUop`: ALU 如何进行计算
- `RegWrite`: 是否写寄存器
- `MemRead`: 是否读内存
- `MemWrite`: 是否写内存
- `MemtoReg`: 写回寄存器的值选择哪一个
- `MemOp`: 读取内存的方式
- `PCsrc`: 如何更新 PC

> 所有的图片都可以点击放大查看

![20231113221650](https://raw.githubusercontent.com/learner-lu/picbed/master/20231113221650.png)

> RISCV 在设计时选择将立即数分散,寄存器编码位置固定, 这样可以使不同指令间拥有尽可能多的共同数据通路,降低指令信号的扇出,提高立即数多路复用水平(简单来说就是 ID 译码很快, 得益于指令的设计和硬件单元的实现, 可以快速拿到信息)

首先在 ID 阶段生成了指令对应的控制信号, 不同的控制信号有对应的功能

- `ALU_Asrc ALU_Bsrc MemtoReg` 这三个信号**对应三个多路选择器(mux)**, 如图中蓝色的单元所示. 它们的功能是有多个输入, 根据信号的状态选择其中一个作为输出
- `ALUop MemOp` 这两个信号会被**传递给 ALU 控制单元 和 存储器控制单元**, 会交给控制单元去处理, 类似 ALU 中的加减乘除等运算, Mem 中的 1/2/4字节读写的选择
- `RegWrite MemRead MemWrite` 这三个信号**仅有 0 和 1 两个状态, 类似于开关**

> PCsrc 并没有在图中画出来, 这个稍微有点复杂, 后文结合跳转指令再提

---

根据这些控制信号可以得出系统在给定指令下的一个周期内所需要做的具体操作, 应该选择哪一个作为输入, 是否应该写, 是否应该读, ALU 做何种计算等等. 这时候我们就可以回答第一个问题 "**其他信息(others)指的是什么?**", 或者与此等价的问题 "**每一阶段的 IR 都保留了哪些值?**"

下图为各阶段 IR 设计, 考虑到流水线设计, 每一阶段 IR 必须包含 **当前阶段所需的所有信息** 以及当前阶段执行后产生的 **下一阶段需要的信息**

![20231113222435](https://raw.githubusercontent.com/learner-lu/picbed/master/20231113222435.png)

#### IF_ID -> ID_EX

IF_ID 只需要保存指令 Instruction 和 PC 的值, 保存 PC 是因为对于跳转指令来说需要**指令对应时刻的 PC 作为跳转起点**.

经由 ID 译码之后将 Instruction 拆分得到了 `rd imm ctl_sig Branch` 这样一些之后阶段需要信息, 同时通过 rs1 和 rs2 从寄存器组中读取得到对应的 ra rb 值, pc 值继承自 IF_ID, **需要注意的是还需要额外保留 rs1 和 rs2, 这是为了后续的数据冒险单元的检测考虑, 后文再做展开**

![20231113222525](https://raw.githubusercontent.com/learner-lu/picbed/master/20231113222525.png)

#### ID_EX -> EX_MEM

EX_MEM 继续继承来自 ID_EX 的 `rb rd imm pc` 等值, 以及控制信号(ControlSignal) 中的 6 个. 这些信息需要在 MEM 和 WB 阶段被使用

> 不直接继承完整的 ControlSignal 而是只保留有效的 6 个是因为 EX 阶段已经使用了其中的 3 个, 从硬件资源的角度来说节省 IR 空间

另外额外保存 ALU 的计算结果 `alu_result`, 以及经过**一个用于判断条件跳转指令是否成立的 Branch Cond 电路** 得到的跳转条件是否成立的 branch_cond

![20231114103614](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114103614.png)

#### EX_MEM -> MEM_WB

MEM_WB 继承来自 EX_MEM 剩余的两个控制信号 `MemtoReg RegWrite` 用于选择写回的内容, 以及判断是否写回, rd 判断写回的地址, 从 MEM 读取的 read_data 值以及另一个可能写回的 alu_result 的值

![20231114103921](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114103921.png)

#### PC(控制冒险)

至此, 全部 5 阶段流水线以及 4 个 IR 的设计都已经介绍完毕. 然后我们再来看一下最麻烦的 PCsrc

更新 PC 一共有 4 种情况

1. 最简单最基本的, 因为 RISCV32I 为32位定长指令集, 所以只需要 PC(IF) + 4 即可
2. 对于 J 型指令 jal, 这是一个无条件跳转指令. **由于 ID 阶段就可以判断出这条指令是 jal 指令, 因此无需再等到 EX 阶段由 ALU 完成计算, 只需要在ID阶段添加一个加法器只用于计算 PC(ID) + imm(ID), 这样就可以节省一个周期的时间(只浪费下一条指令的 IF)**
3. 对于 RISCV 32I 中的 JALR 指令, 其作用是 PC = ra + imm(ID).

   > 除此之外可以看到笔者补全了 `ALU_Asrc` 和 `ALU_Bsrc` 的 mux 的输入, **有且仅当指令是 jal 和 jalr 的时候, 才会选择 ALU_Asrc 为 PC 以及 ALU_Bsrc 为 4**, 因为 jal jalr 除了改变 PC 之外还有 `R[rd] = pc + 4` 的功能

4. 对于 B 型指令, 如果 Branch Cond 电路判断跳转条件为真, 则使用该指令对应的 PC(EX) 和 imm(EX) 计算跳转地址来改变 PC

因此需要添加一个加法器, 加法器有两个输入

- 第一个输入(PC_A), 取决于信号 `PCsrc.A(ID)` `PCsrc.A(EX)` `branch cond` 
  - PC(IF)
  - PC(ID)
  - PC(EX)
  - ra
- 第二个输入(PC_B), 取决于信号 `PCsrc.B(ID)` `PCsrc.B(EX)` `branch cond` 
  - Imm(ID)
  - Imm(EX)
  - 4

![20231114175338](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114175338.png)

根据信号确定加法器的两个输入, 由加法器计算得到更新后的 PC 的值并写回 PC

> 这里其实还有一些小细节, 比如 B/J 完成跳转之后还需要把前面的流水线寄存器清空, 或者在编译阶段添加延迟槽

判断 B 型指令的跳转条件需要使用 Branch Cond 电路, ALU 中会进行一个减法计算. 下图是 X86 指令对应的跳转条件判断(RISV同理), 只需要判断 CF SF ZF OF 这四个标志位即可确定

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20230629132011.png)

#### 数据冒险

由于冯诺依曼体系结构要求指令顺序执行, 但流水线的设计导致读和写的操作分开, 因此数据的同步是一个必须要解决的问题. 我们以如下的指令序列为例

![20231114203944](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114203944.png)

其中指令 1 读取并修改了 r1 寄存器的值, 直到 WB 阶段修改后正确的结果才会被写回寄存器 r1. 但其后四条指令都有 ID 阶段读取使用 r1 寄存器的行为, 如图 ①②③④ 所示

对于 ③, 写入在前半周期, 读取在后半周期, 因此并不会产生冲突. 同理 ④ 也不会有问题. 如下图所示

![20231114205250](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114205250.png)

对于 ①②, 虽然指令 1 在 WB 周期才会写回, 但是实际上在 EX 周期结束之后已经完成了计算, 得到 alu_result 保存在 EX_MEM 中. 因此指令 2 3 虽然在 ID 阶段读取出来的寄存器值是错误的, **但是可以构建一个数据旁路(bypass), 在指令 2 3 EX 阶段之前将正确的结果从后面的 IR 中移动过来, 在 EX 阶段使用正确的值进行计算**. 如下图所示

![20231114210509](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114210509.png)

![20231114222155](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114222155.png)

对于体系结构来说, 需要判断 ID_EX 来的 `rs1 rs2` 与 EX_MEM 的 `rd` 与 MEM_WB 的 `rd` 是否相同(即图中红色单元), 同时需要判断 `RegWrite` 信号为 True(即上条指令是需要写回寄存器的). 如果相同则通过图中蓝色的 bypass 将来自 EX_MEM / MEM_WB 单元的数据传送过来, 需要根据 `Hazard Detection` 的 forwarding 信号来判断选择哪一个最终交给 ALU 进行计算 (有需要额外添加两个 mux)

**但是上述情况是建立在指令 1 在 EX 阶段即可计算完毕得到正确写回结果之上的**, 如果指令 1 是一条 load 指令, **即必须要在 MEM 阶段之后才可以拿到写回结果**, 那么对于指令 3 依然可以使用此 bypass, 但指令 2 无论如何也差一个时钟周期

![20231114220913](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114220913.png)

那么面对这种情况, 只能使流水线暂停一个周期(也成为冒泡 bubble), 

![20231114221437](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114221437.png)

最后再把所有的信号补全, 我们就得到了最终的 ISA 设计

![20231114222700](https://raw.githubusercontent.com/learner-lu/picbed/master/20231114222700.png)

> 最终设计没有说明如何 flush 流水线 IR, 以及如何 bubble; 另外在 jalr 指令中 ra 寄存器也存在数据冒险的问题, 也是需要考虑 bypass 和 bubble 的情况的, 这里也做了省略

## 参考

- [RISC-V控制单元的简单介绍](https://zhuanlan.zhihu.com/p/471466242)
- [RISCV32I CPU](https://nju-projectn.github.io/dlco-lecture-note/exp/11.html)
- [基于RISC-V架构-五级流水线CPU](https://zhuanlan.zhihu.com/p/453232311)
- [基于RISC-V的CPU设计入门__控制冒险](https://www.sunnychen.top/archives/rvintroch)
- [请问RiscV的那种将立即数分散,寄存器编码位置固定,比起传统的cpu,如mips等,有何优缺点?](https://www.zhihu.com/question/405003253)