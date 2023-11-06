
# profiling

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework3.jpg)

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework3.png)

## 运行结果

本实验结果分为两部分, 首先是对于 5 级流水线功能实现的检验

```bash
python src/homework3/test.py
```

运行通过所有测试案例

其中所有测试的的源汇编代码保存在 `asmcode/`, test.py 中每一个测试案例对应相应的汇编代码

```bash
Pass test_CTL1
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

## 实验报告

### 实验分析

本次实验的难度系数还是颇高的, 主要包含三部分任务量

1. 考虑到已经涉及到指令调度和重排, 因此单周期五阶段的 ISA 已经不再适合, 需要完成一个五级流水线的 ISA 实现
2. 需要实现对指令的重排发射
3. 设计性能分析模块

> 第二部分暂时不想考虑实现一个通用型的指令调度算法(~~因为有点难没想好~~), 只考虑实现一个比较简单的依赖图优化算法

### 代码实现

## 参考

- [RISC-V控制单元的简单介绍](https://zhuanlan.zhihu.com/p/471466242)
- [RISCV32I CPU](https://nju-projectn.github.io/dlco-lecture-note/exp/11.html)
- [基于RISC-V架构-五级流水线CPU](https://zhuanlan.zhihu.com/p/453232311)
- [基于RISC-V的CPU设计入门__控制冒险](https://www.sunnychen.top/archives/rvintroch)