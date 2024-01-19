
# cache-coherance

## 多处理器体系结构

提高硬件性能最简单,最便宜的方法之一是在主板上放置多个 CPU.这可以通过让不同的 CPU 承担不同的作业(非对称多处理)或让它们全部并行运行来完成相同的作业(对称多处理,又名 SMP)来完成.有效地进行非对称多处理需要有关计算机应执行的任务的专业知识,而这在 Linux 等通用操作系统中是不可用的.另一方面,对称多处理相对容易实现.

> 相对容易但并不是真的很容易.在对称多处理环境中,CPU 共享相同的内存,因此在一个 CPU 中运行的代码可能会影响另一个 CPU 使用的内存.无法再确定在上一行中设置为某个值的变量仍然具有该值;显然,这样的编程是不可能的.

Symmetrical Multi-Processing,简称SMP,即对称多处理技术,是指将**多CPU汇集在同一总线上,各CPU间进行内存和总线共享的技术**.将同一个工作平衡地(run in parallel)分布到多个CPU上运行,该相同任务在不同CPU上共享着相同的物理内存.

与 SMP 相对应的还有一个叫做 AMP(Asymmetric Multiprocessing), 即非对称多处理器架构的概念.

- SMP的多个处理器都是同构的,使用相同架构的CPU;而AMP的多个处理器则可能是异构的.
- SMP的多个处理器共享同一内存地址空间;而AMP的每个处理器则拥有自己独立的地址空间.
- SMP的多个处理器操通常共享一个操作系统的实例;而AMP的每个处理器可以有或者没有运行操作系统, 运行操作系统的CPU也是在运行多个独立的实例.
- SMP的多处理器之间可以通过共享内存来协同通信;而AMP则需要提供一种处理器间的通信机制.

现今主流的x86多处理器服务器都是SMP架构的, 而很多嵌入式系统则是AMP架构的

在现行的SMP架构中,发展出三种模型:UMA,NUMA和COMA.下面将简单介绍 UMA 和 NUMA 两种模型, 关于 NUMA 的详细内容见 [NUMA](https://luzhixing12345.github.io/klinux/articles/mm/NUMA/)

> 下文讨论的 CPU 是指物理 CPU , 而不是多核 CPU

## UMA

Uniform Memory Access,简称UMA, 即均匀存储器存取模型.**所有处理器对所有内存有相等的访问时间**

![20240119232539](https://raw.githubusercontent.com/learner-lu/picbed/master/20240119232539.png)

既然要连接多个 CPU 和内存, 这种 UMA 的方式很明显是最简单直接的, 但问题也同样明显, **BUS 会成为性能的杀手**. **多个 CPU 需要平分总线的带宽, 这显然非常不利于计算**.

x86多处理器发展历史上,早期的多核和多处理器系统都是UMA架构的.这种架构下, 多个CPU通过同一个北桥(North Bridge)芯片与内存链接.北桥芯片里集成了内存控制器(Memory Controller),

下图是一个典型的早期 x86 UMA 系统,四路处理器通过 FSB (前端系统总线, Front Side Bus) 和主板上的内存控制器芯片 (MCH, Memory Controller Hub) 相连, CPU 通过 PCH 访问内存, DRAM 是以 UMA 方式组织的,延迟并无访问差异. 

> [PCH(Platform Controller Hub)](https://en.wikipedia.org/wiki/Platform_Controller_Hub) 是 Intel 于 2008 年起退出的一系列晶片组,用于取代以往的 I/O Controller Hub(ICH). PCI和PCH在计算机系统中扮演不同的角色,PCI提供了扩展插槽,允许用户通过插入PCI卡来扩展计算机的功能,而PCH则负责管理和控制各种接口和设备的通信.PCI和PCH是不同层次的技术,它们共同工作来实现计算机系统的功能
>
> SMB(System Management Bus):SMB 是一种系统管理总线,用于连接计算机系统中的各种硬件设备和传感器,以进行系统管理和监控.SMB 主要用于与系统管理芯片(如电源管理,温度传感器,风扇控制等)进行通信,提供系统监控,电源管理,硬件调整等功能.它在系统级别提供了对硬件设备的管理和监控功能,而不是直接用于CPU访问内存

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/numa-fsb-3.png)

## NUMA

基于总线的计算机系统有一个瓶颈, 有限的带宽会导致可伸缩性问题.系统中添加的CPU越多,每个节点可用的带宽就越少.此外,添加的CPU越多,总线就越长, 延迟也就越高.

因此在另一种设计方法中, 多处理器采用物理分布式存储器, 称为**分布式共享存储器(distribute share memory, DSM)**. 为了支持更多的处理器, 存储器必须分散在处理器之间, 而不应当是集中式的; 否则, 存储器系统就无法在不大幅延长访问延迟的情况下为大量处理器提供带宽支持. 随着处理器性能的快速提高以及处理器存储器带宽需求的相应增加, 多处理器大多采用分布式存储器的方式

![20240119234515](https://raw.githubusercontent.com/learner-lu/picbed/master/20240119234515.png)

将存储器分散在节点之间, 既增加了带宽, 也缩短了到本地存储器的延迟

因此,AMD 在引入 64 位 x86 架构时,实现了 NUMA 架构.

## 监听协议

![20240118213343](https://raw.githubusercontent.com/learner-lu/picbed/master/20240118213343.png)

> 图源: [天玑9300性能前瞻:发哥太强了!](https://www.bilibili.com/video/BV1dQ4y1J7LC) 1:07


## 参考

- [一小时,完全搞懂 cpu 缓存一致性](https://zhuanlan.zhihu.com/p/651732241)
- [无锁编程_从CPU缓存一致性讲到内存模型](https://zhuanlan.zhihu.com/p/642416997)
- [在线体验 MESI 协议状态转换](https://www.scss.tcd.ie/Jeremy.Jones/VivioJS/caches/MESIHelp.htm)
- [MESI保证了缓存一致性,那么为什么多线程 i++还会有问题?的回答](https://www.zhihu.com/question/619301632/answer/3184265150)
- [用动图的方式,理解 CPU 缓存一致性协议!](https://zhuanlan.zhihu.com/p/468636398)
