
# superscale


## 运行结果

> jupyter 提交版见 [main.ipynb](https://github.com/luzhixing12345/archlab/blob/main/src/homework7/main.ipynb)

运行分为两部分, 首先是对于 PPT 中示例程序的模拟执行

```bash
python src/homework7/main.py
```

> DADDIU 是 MIPS 指令集中的无符号双字加立即数, 这里修改为 ADD, 完整输出见 [base.txt](https://raw.githubusercontent.com/luzhixing12345/archlab/main/src/homework7/base.txt)

然后是本次作业要求的程序

```bash
python src/homework7/hw.py
```

> 完整输出见 [output.txt](https://raw.githubusercontent.com/luzhixing12345/archlab/main/src/homework7/output.txt)

## 实验报告

题目要求有点晦涩, 翻译一下就是

1. 双发射处理器, 三次循环执行, 统计资源利用率
2. 原先的单 ALU 部件现在变为两个, 一个用于地址计算, 一个用于执行 ALU 操作
3. 两条 CDB 总线, 支持同时两条指令的写回 和 数据旁路

## 参考

- [计算机体系结构-超标量乱序CPU微架构(上)](https://zhuanlan.zhihu.com/p/601688983)