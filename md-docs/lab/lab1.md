
# lab1

Cache一致性协议的实现,要求:

- 在监听和目录协议中任选一种模拟
- Cache块的状态(status)自定,所模拟的协议必须是正确的
- 可以模拟教材上的协议,也可以模拟其他文献中的协议
- 处理器个数为4个
- 测试数据集由一组4元项 <Pn, op, addr, value> n in {0,1,2,3}, op in {read, write}
- 输出,给出addr所在块的状态
- Cache块大小不小于32字节,Cache容量不超过32K字节 监听:<Pn, status, value> 目录:addr所在块对应的项<status, bitvector, value>

