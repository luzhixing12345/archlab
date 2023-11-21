
# Tomasulo

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework5.jpg)

## 运行结果

运行标准示例程序, 与前面的 scoreboard 的示例程序相同, 但采用 tomasulo 算法

```bash
python src/homework5/main.py
```

> 完整输出见 [classic_example.txt](https://raw.githubusercontent.com/luzhixing12345/archlab/main/src/homework5/classic_example.txt)

```bash
----------------------------------------------------------------------
[instruction status]

    Op     dest j   k   | Issue  Exec  Write
    Load   F6   34  R2  |     1     3     4
    Load   F2   45  R3  |     2     4     5
    Mul    F0   F2  F4  |     3    15    16
    Sub    F8   F6  F2  |     4     7     8
    Div    F10  F0  F6  |     5    56    57
    Add    F6   F8  F2  |     6    10    11
```

完成本次要求的作业, 三次循环展开

```bash
python src/homework5/loop.py
```

> 完整输出见 [loop.txt](https://raw.githubusercontent.com/luzhixing12345/archlab/main/src/homework5/loop.txt)

```bash
----------------------------------------------------------------------
[instruction status]

    Op     dest j   k   | Issue  Exec  Write
    Load   F0   0   R2  |     1     3     4
    Add    F2   F0  R3  |     2     6     7
    Store  F2   0   R2  |     3     8     9
    Load   F4   -4  R2  |     4     6     7
    Add    F6   F4  R3  |     5     9    10
    Store  F6   -4  R2  |     6    11    12
    Load   F8   -8  R2  |     7     9    10
    Add    F10  F8  R3  |     8    12    13
    Store  F10  -8  R2  |     9    14    15
```

## Tomasulo 算法

### 思路

前文提到的 Scoreboard 算法利用多个功能部件实现指令的发射与乱序执行, 同时由控制单元精确监控各条指令之间数据冒险, 如果出现冲突则依然需要 **暂停发射**, **等待执行结束** 或者 **延迟写回**, 因此导致指令发射停滞,指令流截断, 也大大地影响了处理器性能

那么为了解决上述问题, 我们希望最大限度地挖掘出指令的乱序潜力, **即更有效地处理指令间的数据冒险**. 数据相关有四种,分别是读后读/读后写/写后写/写后读.其中"读后读"不会影响指令的执行,所以提数据相关的时候一般忽略"读后读"

对于 WAW 和 WAR 来说, 其实它们并不是真正的数据冒险, 因为我们可以采用寄存器重命名的方式消除掉这两种冒险, 如下图所示

![20231121105009](https://raw.githubusercontent.com/learner-lu/picbed/master/20231121105009.png)

处理器需要的只不过是这两条指令的计算结果, **这个结果计算出来放在哪里不重要**, 只需要为它找到一个以后可以找到的空位就可以了. 因此"写后写"和"读后写"冒险不是真冒险,没必要为他们阻塞指令的流动

但是实际上"写后读"冒险无法解决,因为后序指令读取的数据由前序指令算得,这个过程有明确的数据依赖.

**Scoreboard算法的问题就是太局限于寄存器的名字**,特别典型的就是记分牌居然会因为写后写冒险而阻塞流水,即记分牌会为一个没用的/马上就被覆盖的旧值而阻塞新值的写入,这个做法在Tomasulo面前着实有些古板和僵硬了. Tomasulo 算法可以在逻辑寄存器之外额外有一组物理寄存器, 即为处理器提供超过逻辑寄存器数量的寄存器

## 参考

- [计算机体系结构-Tomasulo算法](https://zhuanlan.zhihu.com/p/499978902)