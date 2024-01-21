
# multicore

## 动机

### 摩尔定律失效

现代计算机实现技术的基础核心是以晶体管为基本单元的平面集成电路.1965年,摩尔(GordonMoore)在Electronics上撰文,认为集成电路密度大约每两年翻一番,这就是著名的摩尔定律.40多年来,摩尔定律不但印证了集成电路技术的发展,也印证了计算机技术的发展. 下图展示了内存芯片和Intel微处理器的发展变化.

![20240121161124](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121161124.png)

指数式增长速度是非常可怕的, 因此摩尔定律是不可能永远或者长期无限发展下去的,这个定律能维持50余年,已经堪称集成电路设计制造人员创造的奇迹.

但目前时钟频率锁定在 3GHz, 

近些年摩尔定律的速度已经放缓了,很多人声称摩尔定律已经失效、集成电路进入后摩尔时代,但芯片设计制造人员一直在不断改进设计与制造工艺为摩尔定律续命. 未来CPU的发展趋势应该是降低功耗、优化性能设计、提高功效等,而不是单纯的堆叠晶体管数量.

### 性能问题

- 功耗墙
- ILP墙
- 内存墙

-> 在晶体管数量无法提升的情况下如何提高性能 => 多核

## 并行计算

Definition: "A parallel computer is a collection of processing elements that **cooperate and communicate** to solve large problemsfast."

> "并行计算机是处理元件的集合,它们通过**合作和通信**快速解决大型问题.

Parallel architecture = **computing** model + **communication** model

在处理并行任务中, 计算和通信都是很重要的环节, 其中我们重点关注多处理器的通信部分. 通信模型分为两种:

- 共享地址: 通过 load/store 通信, 需要显式同步, 因为接收核心需要知道存储何时发生
- 消息传送: 通过消息通信, 隐式同步, 因为传输消息的时候就已经完成了同步

![20240121114050](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121114050.png)

下文我们重点看一下共享地址的多处理器体系结构的情况

## 多处理器体系结构

提高硬件性能最简单,最便宜的方法之一是在主板上放置多个 CPU.这可以通过让不同的 CPU 承担不同的作业(非对称多处理)或让它们全部并行运行来完成相同的作业(对称多处理,又名 SMP)来完成.有效地进行非对称多处理需要有关计算机应执行的任务的专业知识,而这在 Linux 等通用操作系统中是不可用的.另一方面,对称多处理相对容易实现.

> 相对容易但并不是真的很容易.在对称多处理环境中,CPU 共享相同的内存,因此在一个 CPU 中运行的代码可能会影响另一个 CPU 使用的内存.无法再确定在上一行中设置为某个值的变量仍然具有该值;显然,这样的编程是不可能的.

在共享内存地址又分为两种模式, SMP 和 DSM

- **SMP**(Symmetrical Multi-Processing): 即对称多处理技术,是指将**多CPU汇集在同一总线上,各CPU间进行内存和总线共享的技术**.将同一个工作平衡地(run in parallel)分布到多个CPU上运行,该相同任务在不同CPU上共享着相同的物理内存; 其内存组织是**集中式**的; 内存访问模型是均匀的, 称为 **UMA**(uniform memory access)
- **DSM**(distribute share memory): 即分布式共享存储器, 将存储器分散在节点之间, 各节点的 CPU 有本地的内存和远端内存, 访问时间不均匀; 其内存组织形式是**分布式**的; 内存访问模型是不均匀的, 称为 **NUMA**(non-uniform memory access)

![20240121120723](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121120723.png)

### UMA

Uniform Memory Access,简称UMA, 即均匀存储器存取模型.**所有处理器对所有内存有相等的访问时间**

![20240119232539](https://raw.githubusercontent.com/learner-lu/picbed/master/20240119232539.png)

既然要连接多个 CPU 和内存, 这种 UMA 的方式很明显是最简单直接的, 每个 CPU 访问内存的时间是相同的, 整个模型是完全对称的; 但问题也同样明显, **BUS 会成为性能的杀手**. **多个 CPU 需要平分总线的带宽, 这显然非常不利于计算**.

x86多处理器发展历史上,早期的多核和多处理器系统都是UMA架构的.这种架构下, 多个CPU通过同一个北桥(North Bridge)芯片与内存链接.北桥芯片里集成了内存控制器(Memory Controller),

下图是一个典型的早期 x86 UMA 系统,四路处理器通过 FSB (前端系统总线, Front Side Bus) 和主板上的内存控制器芯片 (MCH, Memory Controller Hub) 相连, CPU 通过 PCH 访问内存, DRAM 是以 UMA 方式组织的,延迟并无访问差异. 

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/numa-fsb-3.png)

### NUMA

基于总线的计算机系统有一个瓶颈, 有限的带宽会导致可伸缩性问题.系统中添加的CPU越多,每个节点可用的带宽就越少.此外,添加的CPU越多,总线就越长, 延迟也就越高.

因此在另一种设计方法中, 多处理器采用物理分布式存储器, 为了支持更多的处理器, 存储器必须分散在处理器之间, 而不应当是集中式的;

![20240120202032](https://raw.githubusercontent.com/learner-lu/picbed/master/20240120202032.png)

将存储器分散在节点之间, 既增加了带宽, 也缩短了到本地存储器的延迟. DSM 多处理器也被称为 NUMA(非一致存储器访问), 这是因为它的**访问时间取决于数据字在存储器的位置.** DSM 的关键缺点是处理器之间传送数据的过程变得复杂了一些, 需要在软件中多花一些力气, 以充分利用分布式存储器提升的存储器带宽.

与UMA不同的是,**在NUMA中每个处理器有属于自己的本地物理内存(local memory),对于其他CPU来说是远程物理内存(remote memory)**.一般而言,访问本地物理内存由于路径更短,其访存时间要更短.

在 SMP(对称多处理技术) 和 DSM(分布式共享存储器) 这两种体系结构中, **线程之间的通信是通过共享地址空间完成的, 存储器的地址统一编码, 任何一个拥有正确寻址权限的处理器都可以向任意存储器位置发出存储器引用**. 共享存储器的含义就是指共享地址空间.

### 指令和数据

单指令多数据 SIMD 和多指令多数据 MIMD

![20240121114417](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121114417.png)

![20240121114511](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121114511.png)

## 参考

- [仙童半导体和"八叛逆"所缔造的硅谷模式](https://www.163.com/dy/article/FLPKHUFL0511FQO9.html)