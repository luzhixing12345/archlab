
# cache-coherance

人们发现使用大型的多级缓存可以充分降低处理器对于存储器带宽的需求, 但是缓存策略总是伴随着数据一致性的问题,通俗的讲是**不同存储节点中同一条数据副本之间不一致的问题**.CPU Cache的存在导致多核CPU中缓存数据与内存数据之间可能存在不一致的情况.

首先思考单核CPU下,何时将缓存数据的修改同步至内存中,使得缓存与内存数据一致?

- **写直达**:CPU每次访问修改数据时,无论数据在不在缓存中,都将修改后的数据同步到内存中,缓存数据与内存数据保持强一致性,这种做法影响写操作的性能.
- **写回**:为了避免每次写操作都要进行数据同步带来的性能损失,写回策略里发生读写操作时:
  - 如果缓存行中命中了数据,写操作对缓存行中数据进行更新,并标记该缓存行为已修改.
  - 如果缓存中未命中数据,且数据所对应的缓存行中存放了其他数据:
    - **若该缓存行被标记为已修改**,读写操作都会将缓存行中现存的数据写回内存中,再将当前要获取的数据从内存读到缓存行,写操作对数据进行更新后标记该缓存行为已修改;
    - **若该缓存行未被标记为已修改**,读写操作都直接将当前要获取的数据从内存读到缓存行.写操作对数据进行更新后标记该缓存行为已修改.

## 缓存一致性问题

假设 CPU1 和 CPU2 同时运行两个线程,都操作共同的变量 a 和 b, 为了考虑性能,使用了我们前面所说的**写回**策略, 把执行结果直接写入到 L1/L2 Cache 中,然后把 L1/L2 Cache 中对应的 Block 标记为脏的,这个时候**数据其实没有被同步到内存**中的,因为写回策略只有在 A 号核心中的这个 Cache Block 要被替换的时候,数据才会写入到内存里.

![20240120203920](https://raw.githubusercontent.com/learner-lu/picbed/master/20240120203920.png)

由于 CPU 1/2 的缓存策略, 导致数据在这个时候是不一致,从而可能会导致执行结果的错误.

那么,要解决这一问题,就需要一种机制,来**同步两个不同核心里面的缓存数据**.要实现的这个机制的话,要保证做到下面这 2 点:

1. 某个 CPU 核心里的 Cache 数据更新时,必须要传播到其他核心的 Cache, 称为**写传播**(Write Propagation);
2. 某个 CPU 核心里对数据的操作顺序,必须在其他核心看起来顺序是一样的, 称为**事务的串形化**(Transaction Serialization).

第一点写传播很容易就理解,当某个核心在 Cache 更新了数据,就需要同步到其他核心的 Cache 里; 第二点事务的串行化指的是不同 CPU 要看到**相同顺序的数据变化**,比如两个线程同时执行 `a=100` 和 `a=200`, 所有其他核心收到的更新变化都应该是相同的, 比如变量 a 都是先变成 100,再变成 200

![20240120210511](https://raw.githubusercontent.com/learner-lu/picbed/master/20240120210511.png)

要实现事务串形化,要做到 2 点:

- CPU 核心对于 Cache 中数据的操作,需要**同步给其他 CPU 核心**;
- 要引入「**锁**」的概念,如果两个 CPU 核心里有相同数据的 Cache,那么对于这个 Cache 数据的更新,只有拿到了「锁」,才能进行对应的数据更新.

## 缓存一致性

在讨论缓存一致性问题的解决方案之前我们先来看一下**一致性的内存系统**的定义: **所有处理器在任何时刻对每一个内存位置的最后一个全局写入值有一个一致的视图**

> all processors, at any time, have consistent view of last globally written value to each location

一致性缓存提供了迁移的能力, 可以将数据项移动到本地缓存中, 并以透明的方式加以使用. 这种迁移既缩短了访问远程共享数据项的延迟, 也降低了对共享存储器的带宽要求.

实现缓存一致性协议的关键在于跟踪数据块的所有共享状态, 目前使用的协议有两类, 分别是**监听协议**(snooping, 也可以叫嗅探)和**目录协议**(directory-based)

### 监听协议

写传播的原则就是当某个 CPU 核心更新了 Cache 中的数据,要把该事件广播通知到其他核心. 与此同时处理器会监听来自总线上广播事件, 如果当前 CPU 的缓存中有该缓存块的副本则应该以某种方式做出反应(更新)

![20240121193905](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121193905.png)

当任何一个 CPU 核心修改了 L1 Cache 中变量的值, 都会通过总线把这个事件广播通知给其他所有的核心. 每个 CPU 核心都会监听总线上的广播事件,并检查是否有相同的数据在自己的 L1 Cache 里面,如果其他 CPU 核心的 L1 Cache 中有该数据,那么也需要把该数据更新到自己的 L1 Cache.

监听协议的实现又分为两种: **写入失效**(write invalid protocal) 和 **写入更新**(write update/boardcast)

#### 写入失效

写入失效指当一个处理器更新 X 的值后, 广播通知所有其他处理器关于 X 的副本 cache 失效

下面是一个写入失效的例子, A B 处理器分别读取 X 的值并保存到 cache 中, 当 A 更新 X 的值后在 bus 上广播 `invalid X` 信号, 所有其他处理器收到该信号后均将其 cache 内 X 的**缓存行的 valid 置为 0**

> 下图中清空了 P_b cache 的值, 实际上只是将其 valid 位置 0 完成失效操作

最后当 B 试图读取 X 的最新值时可以直接从 A cache 当中取到, 并且更新内存中的 X 的值.

![20240121194146](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121194146.png)

对于写入操作我们需要确保执行的处理器拥有独占访问, **禁止任何其他处理器同时写入**. 如果有多台处理器同时尝试写入同一数据, 则只有其中一个将会在**竞争中获胜**(稍后讨论), 因此这一协议实现了写入串行化.

#### 写入更新

写入更新的操作并不会使其他处理器的 cacheline 失效, 它会在每次写入时通知所有其他处理器更新 cache 的数据, 如下图所示

当 A 更新 X 后广播 `update X` 信号, 此时 B 的 cache 和内存中的数据一同更新, 这样所有其他处理器总是可以获取到最新的数据

![20240121195801](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121195801.png)

写入更新的方法要求每次 write 都广播到共享缓存线上, 这无疑会占用相当多的总线带宽, 而且 CPU 需要每时每刻监听总线上的一切活动发出每一个广播事件. 而对于写入失效的方法来说, 在一些情况下的 write 不会广播

> 修改(M)状态下的 write 不需要广播 invalid, 无效(I)状态下不需要监听, 后文 MSI 协议中会提到

### MSI

因此现代多处理器大多选择 **写入失效**(write invalid protocal) 作为监听协议的实现, 后文将会介绍基于写入失效的 MSI write-invalid protocol

MSI 规定了缓存行(cache line)的 `M S I` 三种状态:

- `Modified`: 已修改, 指数据被修改后保存在 cache line 中, 和内存中的数据不一致, 数据只存在于本 cache line 中
- `Shared`: 共享, 指数据和内存中的数据一致, 数据存在于很多 cache 中
- `Invalidated`: 已失效, 指该 cache line 无效

> 其中**同一时刻 M 状态最多只会存在一个**, 而 S 状态可以同时存在很多个

我们可以为每个 cache line 添加一个 `dirty flag` 用于记录是否**已修改且未写回内存**; M S I 三种状态是针对每一个 cache line 的.

![20240122103012](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122103012.png)

这三种状态会随着 **CPU 的 read/write cache 请求**而发生状态的转换, 其中蓝色代表 CPU 的 read 信号, 紫色代表 CPU write 的信号, 黑色表示伴随该请求在 BUS 上广播的信号, 整个状态转换图如下.

![20240121234459](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121234459.png)

该转换图下面我们针对转换图分别描述一下:

- I 状态的 read/write 必然 cache miss
  - 对于 read 转换到 S, 同时广播 `read miss`
  - 对于 write 转换到 M, 同时广播 `write miss`
- S 状态如果 read hit 则保持不变; 如果 write hit 则转换为 M, 同时广播 `invalid` 使其他所有 cache 失效
- M 状态的 read/write hit 都保持在原状态不变, 不发出信号

> 这里书上的图还有关于 S/M 状态的 read/write miss 的箭头, 这里我觉得没有必要画出来, 因为实际上是替换的策略.
> 
> 正常来说 S/M 状态的数据在 cache 中不会 miss, 这里是指对于**另一个地址**(假设为 B)在直接映射的高速缓存中对应的 cache line 和当前某个状态 S/M 的 cache line (假设地址为 A)发生了**地址冲突**, 此时 那么此时需要替换掉 A 的 cache line
>
> - 在 A 的 S 状态下 B 的 CPU read miss 发生后只需要直接替换, 广播 B 的 read miss; B 的状态依旧保持 A 之前的 S
> - 在 A 的 M 状态下 B 的 CPU write miss 发生后需要先写回 A 的 data, 广播 B 的 write miss; B 保持 M 状态
> - 在 A 的 M 状态下 B 的 CPU read miss 发生后需要先写回 A 的 data, 广播 B 的 read miss; B 进入 S 状态

上图表示的是**当前 CPU** 在发出 read/write 请求后对于 cache hit/miss 的情况下当前 cache line 的状态转移图; 下图是位于总线上的**其他 CPU**监听到来自总线的信号后进行的状态转移图

![20240121235254](https://raw.githubusercontent.com/learner-lu/picbed/master/20240121235254.png)

- I 状态无需监听任何信号, 因为本身 cache 就是失效的
- S 状态可能会收到全部的 read miss/ write miss/ invalid 三种信号
  - read miss 时保持 S 不变, 此时共享缓存可以为发生 read miss 的 CPU 提供数据
  - invalid/write miss 的情况相似, 都说明有另外一个 CPU 试图写入(只是一个成功了一个失败了), 所有其他 cache line 进入 I 状态
- M 状态只可能收到两种信号 read miss/ write miss
  - read miss 说明有其他 CPU 试图读, 此时 M 状态中的数据为**最新的值**, 需要先写回 memory 同时尝试同发出信号的 CPU 共享数据, 此时该 cache 的数据不再是唯一的了, 所以进入 S 状态
  - write miss 说明有其他 CPU 试图写入, 此时 M 状态中的数据为**最新的值**, 需要先写回 memory 同时尝试同发出信号的 CPU 共享数据, 因为同一时刻只会有一个 M 状态, 因此该 CPU 进入 I 状态, 让另一个 write 的 CPU 进入 M

> M 状态只会收到 read/write miss 两种信号而不会收到 invalid 信号是因为当一个 cache line 处于 M 状态时, 所有其他的 cache line 应当全部由于写入时的 invalid/write miss 信号进入 I 状态, 因此不可能有处于 S 状态的其他 cache line. 所以不可能发出 invalid 信号

---

我们来看一道例题, 有三个 CPU 1/2/3, 初始都处于无缓存的 I 状态, 对于 t1-t4 时刻的 read/write, 总线上的 bus request 和三个 CPU 的 cache 状态如何变化?

![20240122111449](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122111449.png)

t1 时 CPU1 write A, 此时 CPU1 先从 memory 中读取 A 的值, 更新 cache, 由 I -> M, 并在总线广播 invalid A 信号; 其余 CPU 收到该信号后没有变化(或者说 I 状态不监听信号).

![20240122112617](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122112617.png)

> 这里的 bus request 走的共享缓存总线, 还有数据总线和地址总线用于传输数据, 图中合并到一条 bus 中了没有画出来

t2 时 CPU2 read A, 此时 CPU2 进入 S 状态, 在总线广播 CPU2 read miss; CPU1 收到信号后也转换为 S 状态, 并将自身最新的 A 数据发送给 CPU2, 同时写回内存, 中断 CPU2 的读内存请求; CPU3 不变.

![20240122112813](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122112813.png)

t3 时 CPU3 read A, 此时 CPU3 进入 S 状态, 在总线广播 CPU3 read miss; CPU1/CPU2 收到信号后状态不变, 任意一个都可以将数据共享给 CPU3(图中标记 CPU2 共享数据, 实际上 CPU1 也可以)

![20240122113043](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122113043.png)

t4 时 CPU2 write A, 此时 CPU2 进入 M 状态, 在总线广播 invalid A; CPU1/3 收到信号后进入 I;

![20240122113444](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122113444.png)

尽管这个协议是正确的, 但是它省略了许多复杂的因素, 比如该协议假定操作具有**原子性**, 即在完成一项操作的过程中不会发生任何中间操作. 例如这里假定可以采用单个原子动作形式来检测写入缺失, 获取总线和接收响应, 但现实情况是即使是读取缺失也可能不具备原子性, 非原子性的操作可能会导致死锁, 我们将在 DSM 设计时讨论这些复杂的内容.

### MESI

考虑对于下图的 t1-t4 的操作, 右侧为按照 MSI 协议 P1 P2 cache 的状态转换和 bus request 情况.

![20240122171707](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122171707.png)

可以发现在 t2 和 t4 时刻, 由于写操作导致 S -> M, 此时需要在总线上广播 invalid 信号. 但实际上该操作是不必要的, 因为其实**只有 P1 拥有唯一的 A cache**, 这个信号占用了无效的总线带宽

由此引出了改进的 MESI 协议, 其在 MSI 协议的基础上新增了一个 E 独占状态

- `Modified`: 已修改, 指数据被修改后保存在 cache line 中, 和内存中的数据不一致, 数据只存在于本 cache line 中
- `Exclusive`: 独占, 指数据和内存中的数据一致, 数据只存在于本 cache line 中
- `Shared`: 共享, 指数据和内存中的数据一致, 数据存在于很多 cache 中
- `Invalidated`: 已失效, 指该 cache line 无效

> E 状态仅可能存在在一个高速缓存中, 这意味着相应的处理器可以**直接写入而无需使其他的副本失效**

下图为 MESI CPU request 的状态转移图, 相比 MSI 唯一的区别就是新增了一个 E 状态, S 状态维持不变; I 状态的 read miss 会先转换到 E 状态; **不会因为本机 CPU request 导致 E -> S 的转换, E -> S 的转换是总线的信号引发的**

![20240122182451](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122182451.png)

由于是独享的缓存, 所以 E 状态的 write hit 不会在总线广播 invalid 信号, 这样节约了总线带宽.

BUS request 转换图如下:

![20240122184116](https://raw.githubusercontent.com/learner-lu/picbed/master/20240122184116.png)

MESI 协议非常受欢迎因为他对于大多数的并行编程工作负载都表现得很好, 因为实际上大多情况下进程之间从不/很少通信, 因为不存在数据共享, 因此没有必要使得其他副本失效.

> MOESI 的内容暂时省略

### 目录协议

目录协议指的是所有共享数据块的信息都保存在中央的一个位置, 称为**目录**(directory-base)

## 参考

- [一小时,完全搞懂 cpu 缓存一致性](https://zhuanlan.zhihu.com/p/651732241)
- [无锁编程_从CPU缓存一致性讲到内存模型](https://zhuanlan.zhihu.com/p/642416997)
- [在线体验 MESI 协议状态转换](https://www.scss.tcd.ie/Jeremy.Jones/VivioJS/caches/MESIHelp.htm)
- [MESI保证了缓存一致性,那么为什么多线程 i++还会有问题?的回答](https://www.zhihu.com/question/619301632/answer/3184265150)
- [MESI and MOESI Protocols](https://www.youtube.com/watch?v=nrzT044qNIc)