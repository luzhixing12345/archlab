
# superscale


## 运行结果

> jupyter 提交版见 [main.ipynb](https://github.com/luzhixing12345/archlab/blob/main/src/homework7/main.ipynb)

运行分为两部分, 首先是对于 PPT 中示例程序的模拟执行

```bash
python src/homework7/main.py
```

> DADDIU 是 MIPS 指令集中的无符号双字加立即数, 这里修改为 ADD, 完整输出见 [example.txt](https://raw.githubusercontent.com/luzhixing12345/archlab/main/src/homework7/example.txt)

指令执行流程

```txt
CLOCK 20
[instruction status]

  ID  Instructions     | Issue  Exec   Mem Write | Qj  Qk  stage
  0   LOAD  F0    0 R1 |     1     2     3     4 |         COMPLETE 
  1   FADD  F4   F0 F2 |     1     5           8 |         COMPLETE 
  2   STORE F4    0 R1 |     2     3     9       |         COMPLETE 
  3   ADD   R1   -8 R1 |     2     4           5 |         COMPLETE 
  4   BNE   Loop R1 R2 |     3     6             |         COMPLETE 
  5   LOAD  F0    0 R1 |     4     7     8     9 |         COMPLETE 
  6   FADD  F4   F0 F2 |     4    10          13 |         COMPLETE 
  7   STORE F4    0 R1 |     5     8    14       |         COMPLETE 
  8   ADD   R1   -8 R1 |     5     9          10 |         COMPLETE 
  9   BNE   Loop R1 R2 |     6    11             |         COMPLETE 
  10  LOAD  F0    0 R1 |     7    12    13    14 |         COMPLETE 
  11  FADD  F4   F0 F2 |     7    15          18 |         COMPLETE 
  12  STORE F4    0 R1 |     8    13    19       |         COMPLETE 
  13  ADD   R1   -8 R1 |     8    14          15 |         COMPLETE 
  14  BNE   Loop R1 R2 |     9    16             |         COMPLETE 


[unit]

            Name Func    | status id
     Integer ALU Add     | Free   14
          FP ALU Fadd    | Free   11
```

统计信息

```txt
CLOCK | Integer ALU |      FP ALU | Data Cache | CDB
    1 |             |             |            |
    2 |      0/Load |             |            |
    3 |     2/Store |             |     0/Load |
    4 |       3/Add |             |            | 0/Load
    5 |             |      1/Fadd |            | 3/Add
    6 |       4/Bne |             |            |
    7 |      5/Load |             |            |
    8 |     7/Store |             |     5/Load | 1/Fadd
    9 |       8/Add |             |    2/Store | 5/Load
   10 |             |      6/Fadd |            | 8/Add
   11 |       9/Bne |             |            |
   12 |     10/Load |             |            |
   13 |    12/Store |             |    10/Load | 6/Fadd
   14 |      13/Add |             |    7/Store | 10/Load
   15 |             |     11/Fadd |            | 13/Add
   16 |      14/Bne |             |            |
   17 |             |             |            |
   18 |             |             |            | 11/Fadd
   19 |             |             |   12/Store |
```

然后是本次作业要求的程序

```bash
python src/homework7/hw.py
```

> 完整输出见 [output.txt](https://raw.githubusercontent.com/luzhixing12345/archlab/main/src/homework7/output.txt)

指令执行流程

```txt
CLOCK 16
[instruction status]

  ID  Instructions     | Issue  Exec   Mem Write | Qj  Qk  stage
  0   LOAD  F0    0 R1 |     1     2     3     4 |         COMPLETE 
  1   FADD  F4   F0 F2 |     1     5           8 |         COMPLETE 
  2   STORE F4    0 R1 |     2     3     9       |         COMPLETE 
  3   ADD   R1   -8 R1 |     2     3           4 |         COMPLETE 
  4   BNE   Loop R1 R2 |     3     5             |         COMPLETE 
  5   LOAD  F0    0 R1 |     4     5     6     7 |         COMPLETE 
  6   FADD  F4   F0 F2 |     4     8          11 |         COMPLETE 
  7   STORE F4    0 R1 |     5     6    12       |         COMPLETE 
  8   ADD   R1   -8 R1 |     5     6           7 |         COMPLETE 
  9   BNE   Loop R1 R2 |     6     8             |         COMPLETE 
  10  LOAD  F0    0 R1 |     7     8     9    10 |         COMPLETE 
  11  FADD  F4   F0 F2 |     7    11          14 |         COMPLETE 
  12  STORE F4    0 R1 |     8     9    15       |         COMPLETE 
  13  ADD   R1   -8 R1 |     8     9          10 |         COMPLETE 
  14  BNE   Loop R1 R2 |     9    11             |         COMPLETE 


[unit]

            Name Func    | status id
     Integer ALU Add     | Free   14
          FP ALU Fadd    | Free   11
     Address ALU Integer | Free   12
```

统计信息

```txt
CLOCK | Integer ALU |      FP ALU | Address ALU | Data Cache | CDB
    1 |             |             |             |            |
    2 |             |             |      0/Load |            |
    3 |       3/Add |             |     2/Store |     0/Load |
    4 |             |             |             |            | 3/Add
    5 |       4/Bne |      1/Fadd |      5/Load |            |
    6 |       8/Add |             |     7/Store |     5/Load |
    7 |             |             |             |            | 8/Add
    8 |       9/Bne |      6/Fadd |     10/Load |            | 1/Fadd
    9 |      13/Add |             |    12/Store |    10/Load |
   10 |             |             |             |            | 13/Add
   11 |      14/Bne |     11/Fadd |             |            | 6/Fadd
   12 |             |             |             |    7/Store |
   13 |             |             |             |            |
   14 |             |             |             |            | 11/Fadd
   15 |             |             |             |   12/Store |
```

## 实验报告

所谓"**超标量**"是指 CPU 在一个时钟周期内**获取/执行和提交多条指令**,这个概念和"**标量**"对应,"标量"指 CPU 在一个时钟周期内获取/执行和提交一条指令;

"**乱序**"和"**顺序**"对应,"顺序"的意思是"顺序发射/顺序执行",是指 CPU 按照指令原始顺序逐条发射/逐条执行,而"乱序"就是指"乱序发射/乱序执行"."**超标量**"一般和"**乱序**"搭配,"**标量**"一般和"**顺序**"搭配,前两者是现代高速微处理器所广泛使用的技术.

运用这两种技术的"超标量乱序处理器"可以在每个时钟周期获取多条指令,并在内部并行地一次性乱序执行多条指令.这种特性提高了 CPU 的指令吞吐率,加快了程序的执行速度,让包括程序员和用户在内的每个人都从中获益.

### 实验分析

题目要求有点晦涩, 翻译一下就是

1. 双发射处理器, 三次循环执行, 统计资源利用率
2. 原先的单 ALU 部件现在变为两个, 一个用于地址计算, 一个用于执行 ALU 操作
3. 两条 CDB 总线, 支持同时两条指令的写回 和 数据旁路

以及一些假设

1. 整数指令执行 ALU 需要 1 个周期
2. 浮点数加法 FP.ADD 需要三个周期执行
3. load/store 指令执行和访存**各需要一个周期, 共需要两个周期**
4. 不需要访存的指令可以直接跳过访存阶段
5. 分支预测是**完美**的, **分支指令单发射**

### 代码实现

## 参考

- [计算机体系结构-超标量乱序CPU微架构(上)](https://zhuanlan.zhihu.com/p/601688983)