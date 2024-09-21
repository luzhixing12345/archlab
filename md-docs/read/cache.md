
# cache

计算机软件设计者和计算机用户希望存储器的容量越大越好,速度越快越好,价格越便宜越好.但事实上"容量大、速度快、价格低"的3个要求是相互制约的.我们的解决的办法就是采用多种存储器构成存储器结构层次, 从高层向低层,存储设备变得越来越慢,但同时也变得更大更便宜.

下图是一个经典的计算机存储器结构层次

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228203220.png)

早期计算机系统的存储器层次只有三层,CPU寄存器,DRAM主存储器,磁盘存储.由于CPU和主存之间的频率逐渐增大,由于内存DRAM本身这种存储介质的物理特性的延迟,一条由 CPU 发出的访存指令如果真的要去内存中读写数据实际上需要很多个时钟周期才可以完成

![20240224104307](https://raw.githubusercontent.com/learner-lu/picbed/master/20240224104307.png)

因此系统设计者被迫在CPU寄存器文件和主存之间插入了一个小的SRAM高速缓存,被称为L1高速缓存(一级缓存), 同时我们可以利用程序的时空局部性采用一些预取策略提前将数据和指令读到缓存中, 这样如果CPU可以在更快的缓存中读到数据就不需要再去访问更慢的内存了,也就进而提高了性能

![20240224104219](https://raw.githubusercontent.com/learner-lu/picbed/master/20240224104219.png)

两级存储器之间有四个基本的问题

1. **映像规则**: 当把一个块调入高一层存储器时, 可以放到哪些位置上?
2. **查找方法**: 当所要访问的块在高一层存储器中时, 如何找到该块?
3. **替换算法**: 当发生失效时, 应该替换哪一块?
4. **写策略**: 当进行写访问时, 应进行哪些操作?

下面我们围绕这四个问题来逐一解答一下

## 缓存组织结构

一般而言,高速缓存的结构可以用元组(S,E,B,m)来描述, S指一共有S个高速缓存组,每组E行,每一行中有效的缓存块的个数为B, m为主存物理地址长度(通常为64). 组织结构如下图所示:

> 每一个缓存块的大小都是 1 byte, 缓存块的个数 B 和 S 都是 2 的幂次, 即 `S = 2^s`, `B = 2^b`. 

![20240119110922](https://raw.githubusercontent.com/learner-lu/picbed/master/20240119110922.png)

缓存总大小为 `B x E x S` 字节, 即图中灰色部分.

每一个缓存行除了缓存块还有 1 位有效位, 用于表示这个行是否包含有意义的信息; 以及 t 位标记位.

对于一个虚拟地址, 其在缓存中的地址会被划分成如下格式.

![20240119114604](https://raw.githubusercontent.com/learner-lu/picbed/master/20240119114604.png)

高速缓存一共S组,**一共需要s位(2^s=S)来对应每一组**, 每一行是一个高速缓存行.其中每一行有1位有效位,t位标记位,和B字节的缓存块大小, 因为计算机的地址长度m是确定的(一般32或者64),**B字节大小的缓存块需要b位的偏移量来表示(2^b=B)**, 这里的t是计算出来的, 组索引占用s位, 每一个缓存块索引占 b 位, 所以 `t = m-b-s`, 即**剩余部分都留作 tag 位**

> Cache本质就是一个硬件hash表(Tag RAM)+SRAM(DATA RAM)

## 缓存分类

### 直接映射高速缓存

每个组只有一行(E=1)的高速缓存被称为直接映射高速缓存,这种情况是最容易实现和理解的

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228220428.png)

现在一条加载指令指示CPU从主存地址A中读取一个字,那么此时**高速缓存如何判断此时缓存中是否保存着A地址处那个字的副本呢?**

这个过程被分为三个部分: 组选择 + 行匹配 + 字选择

1. 组选择

   给定地址A,我们可以根据之前计算的t,s,b的数据截取其中s的部分,这是**组索引**,我们将高速缓存看成是一个关于组的移位数据,那么这些组索引位就是一个到这个数组的索引,例如下图中映射到组1

   ![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228220503.png)

2. 行匹配

   上一步中已经选择了某个组,接下来就是确定这一组中是否存在A地址所在的缓存块,**在直接映射高速缓存中这很容易因为只有一行**.

   首先判断**有效位必须为1**,如果没有设置有效位那么这个缓存块是没有意义的.接着**截取A地址中的标记t,与缓存块中的标记t判断**,如果相同则说明缓存命中.否则缓存不命中

   ![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228220705.png)

3. 字选择

   最后一步就是根据b在缓存块B中找到对应的位置,这里的**b就是块偏移**,如上图所示

   每个缓存行会缓存 B 个块, b 位地址可以索引对应的块, 对于不同的类型数据(char short int)只需要依次索引(1/2/4)个缓存块即可

---

我们这里假设有如下的一个高速缓存,(S,E,B,m)=(4,1,4,8),换句话说高速缓存有4个组(S),s=2,每个组一行(E=1),每个块两个字节(b=2),地址8位(m=8), 则该缓存的结构如下图所示

> 计算可得 tag 位的长度 t = 8-2-2 = 4

![20240119161850](https://raw.githubusercontent.com/learner-lu/picbed/master/20240119161850.png)

那么此时如果我们要读取地址 `0x00000101` 的 1 字节数据, 流程如下:

1. 划分地址, 找到 tag, set, offset 的部分, 根据 set index 找到对应的缓存组
2. 判断 valid 有效位为 1, 说明其是一个有效的缓存块, 若为 0 则认为缓存失效
3. 判断 tag `0000` 和该缓存行的 tag `0000` 是否相同, 如果相同则说明是相同的数据, 否则无效
4. 取出数据

![20240119162653](https://raw.githubusercontent.com/learner-lu/picbed/master/20240119162653.png)

但是我们发现对于另一个地址 `0x00100101` 地址来说, 其 set index 与 `0x00000101` 相同, 也会映射到这个组. 此时 **tag 不匹配发生缓存不命中, 需要再去内存中取数据, 然后使用新的数据更新缓存行**, 新的 tag 新的 data

![20240119163751](https://raw.githubusercontent.com/learner-lu/picbed/master/20240119163751.png)

那这种时候如果上一个地址又来取数据了那么又会造成一次 cache miss, 频繁的替换 cache, 相当于每次访问数据都要从主存中读取, 这种现象叫做 cache 颠簸(cache thrashing)

### 组相联高速缓存

直接映射高速缓存冲突不命中造成的问题源于**每个组只有一行**, 那么我们自然可以想到**每一个组设置多个缓存行**, 这就是组相联高速缓存

组选择和字选择阶段都没有变化,唯一的区别就是在行选择的阶段,由于有多行,所以进行有效位和标记位判断的时候需要扫描所有行

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228230211.png)

1. 通过 set index 找到对应的组
2. 依次判断组内所有的缓存行, 如果 valid 且 tag 相同, 则取数据
3. 否则发生缓存不命中, 去内存中找, 选择一个缓存行进行更新

这也是 cache 最常用的实现方式

### 全相联高速缓存

全相联是指所有的组全部连接在一起, 直接省去了 S 的部分, 全相联中S=1,只有唯一的一个组,此时E=C/B, 如下图所示

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228230350.png)

且因为S=1,所以s=0,所以地址被划分为标记位和偏移量

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228230525.png)

其他选择方式与组相联完全相同,甚至砍掉了**第一步的组选择, 直接搜索所有行**

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228230534.png)

因为高速缓存电路必须**并行的遍历所有行,匹配所有标记位**,所以构造一个又大又快的相联高速缓存困难且昂贵,因此**全相联高速缓存指适合做小的高速缓存, 例如虚拟内存中的快表TLB**

## 地址访问

我们一直避开了一个关键问题.我们都知道cache控制器根据地址查找判断是否命中,这里的地址究竟是虚拟地址(VA)还是物理地址(PA)呢?

关键就在于 CPU 是使用 VA 直接访问 cache 还是先经过 MMU 得到 PA 再访问 cache 

### VIVT

我们先来介绍一下最符合直觉也是处理起来最简单的**VIVT**(Virtual Index Virtual Tag), 即使用虚拟地址Index域和虚拟地址Tag域. 这种 cache 硬件设计简单.在cache诞生之初,大部分的处理器都使用这种方式.虚拟高速缓存以虚拟地址作为查找对象

![20240720231322](https://raw.githubusercontent.com/learner-lu/picbed/master/20240720231322.png)

虚拟地址直接送到cache控制器,如果cache hit.直接从cache中返回数据给CPU.如果cache miss,则把虚拟地址发往MMU,经过MMU转换成物理地址,根据物理地址从主存(main memory)读取数据.由于我们根据虚拟地址查找高速缓存,所以我们是用虚拟地址中部分位域作为索引(index),找到对应的的cacheline.然后根据虚拟地址中部分位域作为标记(tag)来判断cache是否命中.

这种情况的好处在于 **CPU直接生成的地址可用于获取数据,从而大大缩短了命中时间**. 毕竟MMU转换虚拟地址需要时间.同时 cache 硬件设计也更加简单. 但是,正是使用了虚拟地址作为tag和index,所以引入很多软件使用上的问题. 操作系统在管理高速缓存正确工作的过程中,主要会面临两个问题.**歧义**(ambiguity)和**别名**(alias).为了保证系统的正确工作,操作系统负责避免出现歧义和别名

**歧义(ambiguity)**指**不同的数据在cache中具有相同的tag和index**, 我们知道每个进程都有自己的逻辑(虚拟)地址空间, 由进程的页表负责完成虚拟地址到物理地址的转换. 因此当发生进程上下文切换时, cache 中的数据对于新进程来说没有意义, 如果此时访问虚拟地址可能由于 cache hit 导致错误的结果. 因此需要刷新 cache, 所以**每个上下文切换都会出现大量缓存未命中**, 这非常耗时且低效

**别名(alias)**指**同一个物理地址的数据被加载到不同的cacheline中**. 什么情况下会产生这种情况呢? 例如共享内存, 此时多个虚拟地址同时映射到同一个物理地址, 对应的是同一份数据. 但是由于采用虚拟地址的 index 映射到不同的 cache 组中.

如下图所示, 假如此时修改 mem[VA1], 那么就修改了 cache[VA1] 的数据, 但是再去读 mem[VA2] 的时候虽然得到的还是之前错误的数据.

![20240721001213](https://raw.githubusercontent.com/learner-lu/picbed/master/20240721001213.png)

那么如何解决别名的问题呢, 有两种解决办法, 一种是在页表中使用 `nocache` 不通过 cache. 但是这样就损失了cache带来的性能好处. 另一种方式是**在建立共享数据映射时保证每次分配的虚拟地址都索引到相同的cacheline**, 这样虽然虚拟地址不同但是还是映射到同一个 cacheline, 保证了数据一致性

> 这里的 nocache 对应在 [虚拟地址转换](../mm/虚拟地址转换.md) 的页表格式中低 12 位 flags 的 PCD(page cache disable)

### PIPT

基于对VIVT高速缓存的认识,我们知道VIVT高速缓存存在**歧义**和**别名**两大问题.主要问题原因是tag取自虚拟地址导致歧义,index取自虚拟地址导致别名.

> 使用虚拟地址导致频繁的 cache 冲突造成歧义, 需要刷新 cache 影响性能; 共享内存的多个虚拟地址 index 不同映射到不同的 cacheline 导致同一个物理地址在 cache 中保存多份不一致的数据, 产生别名.

所以最简单的方法是tag和index都取自物理地址.物理的地址tag部分是独一无二的,因此肯定不会导致歧义.而针对同一个物理地址,index也是唯一的,因此加载到cache中也是唯一的cacheline,所以也不会存在别名.我们称这种cache为物理高速缓存,简称**PIPT**(Physically Indexed Physically Tagged)

在这种情况下 CPU 需要先通过 MMU 将虚拟地址转换为物理地址.

在 [虚拟地址转换](../mm/虚拟地址转换.md) 中我们介绍了虚拟地址转换为物理地址的顺序

- 检查 Transition Look Aside Buffer (TLB) 中的逻辑地址,如果 TLB 中存在该地址,请从 TLB 中获取页面的物理地址
- 如果不存在,请从物理内存访问页表,然后使用页表获取物理地址

![20240720232535](https://raw.githubusercontent.com/learner-lu/picbed/master/20240720232535.png)

对于 PIPT 的方式, 每一次查询时都需要完成 MMU 转换, 一旦 TLB miss 那么还需要经历页表遍历的过程去进行地址翻译, 耗时较长.

PIPT 采用唯一的物理地址来做 tag 和 index, 软件层面基本不需要任何的维护就可以避免歧义和别名问题.这是PIPT最大的优点.现在的CPU很多都是采用PIPT高速缓存设计.在Linux内核中,可以看到针对PIPT高速缓存的管理函数都是空函数,无需任何的管理.

### VIPT

观察 PIPT 的模式, 整个 cache 的查询流程为

- VA 通过 MMU 转换得到 PA
- 在 cache 中查 PA 对应的数据

为了提升cache查找性能,我们**不想等到虚拟地址转换物理地址完成后才能查找cache**.因此,我们可以使用虚拟地址对应的index位查找cache,与此同时(硬件上同时进行)将虚拟地址发到MMU转换成物理地址.当MMU转换完成,同时cache控制器也查找完成,此时比较cacheline对应的tag和物理地址tag域,以此判断是否命中cache.我们称这种高速缓存为**VIPT**(Virtually Indexed Physically Tagged)

VIPT 缓存使用来自物理地址的标记位和索引作为来自逻辑/虚拟地址的索引.使用虚拟地址搜索缓存,并获取物理地址的标记部分.使用虚拟地址搜索 TLB,并获取物理地址.最后,将从VIPT缓存获取的物理地址的标签部分与从TLB获取的物理地址标签进行比较.如果它们都相同,则为缓存命中,否则为缓存未命中

![20240721004820](https://raw.githubusercontent.com/learner-lu/picbed/master/20240721004820.png)

VIPT 会存在歧义和别名的问题么? 答案是**一定不存在歧义, 可能存在别名**

VIPT 的 cache 设计和一半的 cache 有所不同. 普通的 cacheline 的 tag 位的长度是按照 cache 的 tag/index/offset 地址划分后的长度. 但是 VIPT 中我们注意到此时匹配的 tag 是由 VPN 经 MMU 转换后得到的 PPN, 因此 **VIPT的 tag 取决于物理页大小的剩余位数,而不是去掉index和offset的剩余位数**.物理tag是唯一的,所以不存在歧义

> 下图中的 (VPN+VPO) 和 (tag/index/offset) 的两个地址是一样的, 只不过是不同的地址划分方式

![20240721012729](https://raw.githubusercontent.com/learner-lu/picbed/master/20240721012729.png)

由于采用虚拟地址作为index,所以可能依然存在别名问题.是否存在别名问题,需要考虑cache的结构,我们需要分情况考虑.

![20240721015946](https://raw.githubusercontent.com/learner-lu/picbed/master/20240721015946.png)

**是否存在别名问题主要取决于 index 域是否全部在 0-11 位**(4KB(12bit位宽)大小为页面进行物理内存管理)

如果 index 域位于地址的bit0~bit11, 因为虚拟地址和物理地址的低 12 位(VPO/PPO)是完全相同的, 而 tag 还是由 MMU 转换来的唯一的物理地址 tag, 因此这种情况 VIPT 和 PIPT 是完全相同的, 多个虚拟地址映射到同一个 cacheline 从而没有别名问题

但是如果 index 部分超越了 bit11 或者全部超越了 bit11(即情况2/3), 那么此时低于 12 位的相同, 但是高于 12 位的部分的虚拟地址仍然可能不同, 因此 index 不一定相同, 可能会映射到不同的 cache 组中. 产生别名问题

> 因此只要 cache 容量小于 4KB, 即 index + offset 低于12位就不会产生别名问题

因此,在建立共享映射的时候,**返回的虚拟地址都是按照cache大小对齐的地址**,这样就没问题了.如果是多路组相连高速缓存的话,返回的虚拟地址必须是满足一路cache大小对齐.**在Linux的实现中,就是通过这种方法解决别名问题**.

---

按照排列组合来说,应该还存在一种PIVT方式的高速缓存.因为PIVT没有任何优点,却包含以上的所有缺点.你想想,PIVT方式首先要通过MMU转换成物理地址,然后才能根据物理地址index域查找cache.这在速度上没有任何优势,而且还存在歧义和别名问题.因此它从来就没出现过.

总的来说, **VIVT Cache问题太多**,软件维护成本过高,是最难管理的高速缓存.所以现在基本只存在历史的文章中.现在我们基本看不到硬件还在使用这种方式的cache.**现在使用的方式是PIPT或者VIPT**.如果多路组相连高速缓存的一路的大小小于等于4KB,一般硬件采用VIPT方式,因为这样相当于PIPT,岂不美哉.当然,如果一路大小大于4KB,一般采用PIPT方式,也不排除VIPT方式,这就需要操作系统多操点心了

## 高速缓存的写

高速缓存的读比较容易,但是写的情况就要复杂很多了.

假设我们要写一个已经缓存了的字(写命中,write hit),在告诉缓存更新它的副本w之后应该如何更新w在层次结构中低一层的副本呢?

最简单的办法称为**写直达(write-through)**,就是立即**将w的高速缓存块写回到低一层中**,但是缺点是每次写回都会引起总线流量.

另一种办法称为**写回(write back)**,**尽可能地推迟更新,只有当替换算法要驱逐这个更新过的块时才把它写回到低一层中**. 由于局部性,写回能显著的减少总线流量,但是它的缺点是增加了复杂性,高速缓存必须为每个高速缓冲行**维护一个额外的修改位(dirty bit)**表明这个高速缓冲块是否被修改过

另一个问题就是如何处理写不命中(write miss),一种方法称为写分配(write allocate),加载相应的低一层的块到高速缓冲,然后更新这个高速缓冲块.但是缺点是每次不命中都会导致一个块从低一层传送到高速缓冲.

另一种方法称为非写分配(not write allocate),避开高速缓冲,直接把这个字写到低一层中

![20240221111201](https://raw.githubusercontent.com/learner-lu/picbed/master/20240221111201.png)

## 真实的高速缓存层次

目前我们一直假设高速缓存中只保存程序数据,但事实上高速缓存除了保存数据也保存指令.保存指令的高速缓存称为i-cache,保存程序数据的高速缓存称为d-cache,既保存指令又保存数据的高速缓存称为统一的高速缓存

现代处理器包括独立的i-cache和d-cache,这样做有很多原因,有两个独立的高速缓存,处理器可以同时读一个指令字和一个数据字.i-cache通常是只读的,因此比较简单,并且可以针对不同的访问模式优化这两个高速缓存,可以有不同的块大小,相联度和容量

下图是Intel Core i7处理器的高速缓存层次,每个CPU芯片有四个核,每个核有自己私有的L1 i-cache L1 d-cache和L2统一高速缓存,所有核共享L3统一高速缓存,这里的一个有趣的特性是所有的SRAM高速缓存都在CPU芯片上

![image](https://raw.githubusercontent.com/learner-lu/picbed/master/20221228235118.png)

现在的处理器一般是有三级缓存,每个核心上有两级缓存,然后所有核心共享一个大的L3缓存,L1还额外按功能划分为指令的缓存和数据的缓存

![20240118215340](https://raw.githubusercontent.com/learner-lu/picbed/master/20240118215340.png)

cahe的速度在一定程度上同样影响着系统的性能, 等级越高,速度越慢,容量越大.但是速度相比较主存而言,依然很快.不同等级cache速度之间关系如下

![20240720220406](https://raw.githubusercontent.com/learner-lu/picbed/master/20240720220406.png)

不同大小核的缓存大小也可能不相同

![20240118213517](https://raw.githubusercontent.com/learner-lu/picbed/master/20240118213517.png)

可以直接使用如下指令查看当前系统的缓存大小

```bash
$ lscpu
Caches (sum of all):
  L1d:                   384 KiB (8 instances)
  L1i:                   256 KiB (8 instances)
  L2:                    10 MiB (8 instances)
  L3:                    24 MiB (1 instance)
```

也可以直接查看 `/sys/devices/system/cpu/cpu0/cache/index0` 下的文件

![20240528154658](https://raw.githubusercontent.com/learner-lu/picbed/master/20240528154658.png)

这里显示 CPU 的 L1 缓存, 总大小 48K, 12 路组相联, 64 组, 每个缓存行大小 64B, 1 级缓存

> physical_line_partition 表示物理行分区,这个参数表示缓存行可以被分割成多少个物理分区.在这个例子中,物理分区数是1,意味着缓存行没有被进一步分割
>
> 12\*64\*64=48KB

## 参考

- [Cache知识记录](https://www.cnblogs.com/DF11G/p/17214206.html)
- [Cache的相关知识(二)](https://www.cnblogs.com/jianhua1992/p/16852781.html)
- [Cache Line操作和Cache相关概念介绍](https://www.cnblogs.com/gujiangtaoFuture/articles/11163844.html)
- [天玑 9300 架构测试既 vivo X100 系列体验报告](https://zhuanlan.zhihu.com/p/668289721)
- [天玑9300性能前瞻:发哥太强了!](https://www.bilibili.com/video/BV1dQ4y1J7LC)
- [每个程序员都应该了解的硬件知识](https://zhuanlan.zhihu.com/p/690189852)
- [Cache的基本原理](https://zhuanlan.zhihu.com/p/102293437)