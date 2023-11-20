
# Tomasulo

![image](https://raw.githubusercontent.com/luzhixing12345/archlab/main/img/homework5.jpg)

## 运行结果

标准示例程序

```bash
python src/homework5/main.py
```

> 完整输出见 [classic_example.txt](https://raw.githubusercontent.com/luzhixing12345/archlab/main/src/homework5/classic_example.txt)

```bash
----------------------------------------------------------------------
[#instruction status#]

    Op     dest j   k   | Issue  Exec  Write
    Load   F6   34  R2  |     1     3     4
    Load   F2   45  R3  |     2     4     5
    Mul    F0   F2  F4  |     3    15    16
    Sub    F8   F6  F2  |     4     7     8
    Div    F10  F0  F6  |     5    56    57
    Add    F6   F8  F2  |     6    10    11


[#functional unit status#]

    Time   Name    | Busy  Op    Vj    Vk    Qj      Qk      A
           Load1   |   No                                    
           Load2   |   No                                    
           Load3   |   No                                    
           Store1  |   No                                    
           Store2  |   No                                    
           Store2  |   No                                    
           Add1    |   No                                    
           Add2    |   No                                    
           Mult1   |   No                                    
           Mult2   |   No                                    


[#register result status#]

             F0 F2 F4 F6 F8 F10 
   Cycle 57  
```

本题程序

```bash
python src/homework5/loop.py
```

> 完整输出见 [loop.txt](https://raw.githubusercontent.com/luzhixing12345/archlab/main/src/homework5/loop.txt)

```bash
----------------------------------------------------------------------
[#instruction status#]

    Op     dest j   k   | Issue  Exec  Write
    Load   F0   0   R2  |     1     3     4
    Add    F2   F0  R3  |     2     6     7
    Store  F2   0   R2  |     3     5     6
    Load   F4   -4  R2  |     4     6     7
    Add    F6   F4  R3  |     5     9    10
    Store  F6   -4  R2  |     6     8     9
    Load   F8   -8  R2  |     7     9    10
    Add    F10  F8  R3  |     8    12    13
    Store  F10  -8  R2  |     9    11    12


[#functional unit status#]

    Time   Name    | Busy  Op    Vj    Vk    Qj      Qk      A
           Load1   |   No                                    
           Load2   |   No                                    
           Load3   |   No                                    
           Store1  |   No                                    
           Store2  |   No                                    
           Store2  |   No                                    
           Add1    |   No                                    
           Add2    |   No                                    
           Mult1   |   No                                    
           Mult2   |   No                                    


[#register result status#]

             F0 F2 F4 F6 F8 F10 
   Cycle 13                     
```

## 参考

- [计算机体系结构-Tomasulo算法](https://zhuanlan.zhihu.com/p/499978902)