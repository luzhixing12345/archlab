
# scoreboard

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework4.png)

运行

```bash
python src/homework4/main.py
```

> 输出结果很多, 仅展示部分内容, 完整内容见 [output.txt](https://github.com/luzhixing12345/archlab/blob/main/src/homework4/output.txt)

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

## 实验报告

TODO

## 参考

- [计算机体系结构-记分牌ScoreBoard](https://zhuanlan.zhihu.com/p/496078836)
