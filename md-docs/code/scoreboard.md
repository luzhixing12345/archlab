
# scoreboard

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework4.png)

运行

```bash
python src/homework4/main.py
```

> 输出结果很多, 仅展示部分内容(clock1 和 clock62 的输出), 完整内容见 [output.txt](https://github.com/luzhixing12345/archlab/blob/main/src/homework4/output.txt)

```txt
----------------------------------------------------------------------
[#instruction status#]

    Op   dest j   k  | Issue  Read  Exec  Write
    Load F6   34  R2 |     1
    Load F2   45  R3 |
    Mul  F0   F2  F4 |
    Sub  F8   F6  F2 |
    Div  F10  F0  F6 |
    Add  F6   F8  F2 |


[#functional unit status#]

    Time   Name    | Busy  Op    Fi  Fj  Fk  Qj      Qk      Rj  Rk
     1/1   Integer |  Yes  Load  F6      R2                  Yes Yes
           Mult1   |   No                                    No  No
           Mult2   |   No                                    No  No
           Add     |   No                                    No  No
           Divide  |   No                                    No  No


[#register result status#]

             F0 F2 F4 F6      F8 F10
   Cycle 1            Integer

.
.
.

----------------------------------------------------------------------
[#instruction status#]

    Op   dest j   k  | Issue  Read  Exec  Write
    Load F6   34  R2 |     1     2     3     4
    Load F2   45  R3 |     5     6     7     8
    Mul  F0   F2  F4 |     6     9    19    20
    Sub  F8   F6  F2 |     7     9    11    12
    Div  F10  F0  F6 |     8    21    61    62
    Add  F6   F8  F2 |    13    14    16    17


[#functional unit status#]

    Time   Name    | Busy  Op    Fi  Fj  Fk  Qj      Qk      Rj  Rk
           Integer |   No                                    No  No
           Mult1   |   No                                    No  No
           Mult2   |   No                                    No  No
           Add     |   No                                    No  No
           Divide  |   No                                    No  No


[#register result status#]

             F0 F2 F4 F6 F8 F10
   Cycle 62
```

## ScoreBoard 算法

### 背景

> 下面先来介绍一下 scoreboard 算法本身, 再来介绍一下笔者的类设计思路和代码运行逻辑

现代的高性能处理器基本都支持多发射和乱序执行,但处理器受到**数据冒险**的影响并不能轻易地实现乱序,所以业界提出了诸如 scoreboard 算法来控制这个过程

顺序执行要求指令一条接一条地流过各个流水段, 如果一条指令被阻塞,那么它后面的指令也被阻塞,即使后面的指令完全可以继续运算而不受被阻塞指令的影响.所以聪明的设计师想到要开几条"近道",好让后面的指令能绕过恰过前面的指令,从而继续执行.

> 例如当执行需要时间很长的访存指令 lw , 我们不希望下一条无关指令等待 lw 的 cache miss/data miss, 或者不需要等待一条耗时很长的 divid 除法运算

但在传统的五级流水线中,运算通路只有一条,每一条指令都需要依次通过处理器中的 ALU /存储器等部件,这个设定有一个言下之意,**就是所有指令都按照一个计算流进行工作**

但这不是事实.**事实是不同类型的指令有不同的计算要求**,前面的例子中 lw 指令需要 ALU 和存储器,**但是后面的一连串计算指令不需要访问存储器,所以它们完全可以绕过存储器继续执行,但是因为五级流水线中设计每条指令都要经过存储器,所以后面的计算指令不得不等着 lw 把存储器让出来.**

因此, 我们希望

1. 每一条指令都可以去选择所需的执行阶段, 例如 lw 需要全部的 IF ID EX MEM WB 阶段, 但 addi 只需要 IF ID EX WB (即跳过访存 MEM 阶段);
2. 与此同时, 计算指令也有各种各样的计算要求以及耗时 (例如浮点数除法的计算周期要远多于普通整数加法计算周期), 加法/乘法/除法指令所需要的计算部件肯定也是不一样的, 我们也期望可以使用不同的计算部件完成对应指令的计算

在五级流水线中只有一个配置,而乱序执行要求,实现"多配置"的流水线处理器, 为各种指令做个性化的配置, 以实现乱序执行.

### 算法流程

scoreboard 其本质是使用一个类似表格的信息存储单元, 通过在指令流水线中为每个指令维护一个"分数牌"(scoreboard),以实现指令的并发执行和解决数据依赖关系.通过分析指令的操作数和状态信息, 动态调度指令的执行

scoreboard 有两个重要的组成部分, 第一部分是 **功能单元状态**, 里面的 9 个状态非常关键, 其代码表示和含义

- Busy: 单元是否繁忙
- Op: 部件执行的指令类型
- F_i: 目的寄存器
- F_j: 源寄存器
- F_k: 源寄存器
- Q_j: 如果源寄存器 F_j 不可用, 部件该向哪个功能单元要数据
- Q_k: 如果源寄存器 F_k 不可用, 部件该向哪个功能单元要数据
- R_j: 源寄存器 F_j 是否可读
- R_k: 源寄存器 F_k 是否可读

![20231112091956](https://raw.githubusercontent.com/learner-lu/picbed/master/20231112091956.png)

> 现在这里可能有些抽象, 稍后笔者会结合具体的示例做解释

第二部分是 **寄存器结果状态**. 里面主要记录对于某一个寄存器,是否有部件正准备写入数据.

![20231112091926](https://raw.githubusercontent.com/learner-lu/picbed/master/20231112091926.png)

> 例如上图中 F4 对应 Mult1,这就表明乘法单元1的计算结果将要写入 F4.

---

CDC6600 处理器执行分为四个阶段, 即发射(issue), 读取(read), 执行(exec), 写回(write back)

再来看一下我们要执行的指令, 一共六条, 如下所示. 其中的前向数据关联和后向数据关联都以及在图中标记出来了

![20231112092443](https://raw.githubusercontent.com/learner-lu/picbed/master/20231112092443.png)

> 这几条指令的寄存器关联程度很高, 很适合作为数据冒险的示例来展示 scoreboard 算法的处理方式

计算处理单元有 5 个

- 1 个访存单元 Integer (我也不知道为什么要叫 Integer)
- 2 个乘法单元 Mult1, Mult2
- 1 个加法单元 Add (减法运算也由加法单元执行)
- 1 个除法单元 Divide

### CLOCK 0

![20231112135516](https://raw.githubusercontent.com/learner-lu/picbed/master/20231112135516.png)

初始状态如上图所示, 所有指令都未发射, 所有功能单元都空闲, 所有寄存器空闲

## 实验报告

### 实验分析

本次实验相对比较独立, 要求完成 scoreboard 算法的代码实现, 和之前写的流水线代码也没有相关性, 所以基本相当于重写

> 好在只是要求模拟算法本身的执行流程, 并不要求真正完成计算, ~~不然真麻烦的要死~~

## 参考

- [计算机体系结构-记分牌ScoreBoard](https://zhuanlan.zhihu.com/p/496078836)
