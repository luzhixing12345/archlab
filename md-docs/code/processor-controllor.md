
# processor-controllor

作业要求:

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework2_full.png)

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework2.jpg)

运行

```bash
python src/homework2/main.py
```

## 实验报告

### 实验分析

第二次作业和第一次作业关联性很大, 也是在初始指令集架构的基础上进行扩展, 完成几组类型的指令

1. 分支指令
2. 跳转指令
3. 寄存器 & 寄存器的运算指令
4. 寄存器 & 立即数的运算指令
5. 访存指令

### RISCV-32I 指令集回顾

RV32I指令集中包含了40条基础指令,涵盖了整数运算/存储器访问/控制转移和系统控制几个大类.本实验中无需实现系统控制的ECALL/EBREAK/内存同步FENCE指令及CSR访问指令,**所以共需实现37条指令**

RV32I的指令编码非常规整,分为六种类型,其中四种类型为基础编码类型,其余两种是变种:

![20231022111521](https://raw.githubusercontent.com/learner-lu/picbed/master/20231022111521.png)

#### R 型指令(10)

寄存器操作数指令,含2个源寄存器rs1,rs2和一个目的寄存器rd

![20231022092118](https://raw.githubusercontent.com/learner-lu/picbed/master/20231022092118.png)

#### I 型指令(15)

立即数操作指令,含一个源寄存器和一个目的寄存器和一个12bit立即数操作数

![20231022105039](https://raw.githubusercontent.com/learner-lu/picbed/master/20231022105039.png)

#### S 型指令(3)

存储器写指令,含两个源寄存器和一个12bit立即数

![20231022105758](https://raw.githubusercontent.com/learner-lu/picbed/master/20231022105758.png)

#### B 型指令(6)

跳转指令,实际是S-Type的变种.与S-Type主要的区别是立即数编码

![20231022105851](https://raw.githubusercontent.com/learner-lu/picbed/master/20231022105851.png)

#### U 型指令(2)

长立即数指令,含一个目的寄存器和20bit立即数操作数

![20231022112108](https://raw.githubusercontent.com/learner-lu/picbed/master/20231022112108.png)

#### J 型指令(1)

长跳转指令,实际是U-Type的变种

![20231022112146](https://raw.githubusercontent.com/learner-lu/picbed/master/20231022112146.png)

### RISCV-32I 汇编指令格式

了解所有的 37 条指令之后就需要手动编写汇编指令, 然后利用 GNU 的工具编译为机器代码以及查看反汇编二进制形式

```bash
sudo apt-get install gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu
```

寄存器出现顺序是 rd > rs2 > rs1, 例如 `Inst rd, rs2, rs1`, 立即数括号括起来, 如 `Inst a0, 100(a1)`

![20231022220910](https://raw.githubusercontent.com/learner-lu/picbed/master/20231022220910.png)

> 寄存器表, 我们这里只用 a0-a7 应该就够了

```bash
riscv64-linux-gnu-gcc example.S -o 
```

## 参考

- [sunnychen riscvbasic](https://www.sunnychen.top/archives/riscvbasic)
- [ica123 5259](https://ica123.com/archives/5259)
- [RISCV 32I CPU](https://nju-projectn.github.io/dlco-lecture-note/exp/11.html)