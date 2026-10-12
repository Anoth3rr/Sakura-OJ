# 数字炸弹：testlib 交互题代码

约束：`1 <= T <= 200000`，`1 <= x <= n <= 10^9`，单个测试文件 `sum(n) <= 10^9`。
每组最多 100 次 `?`；`!` 不计入查询次数。

## 隐藏数据和交互协议

生成器输出的隐藏 `.in` 格式为：

```text
T
n_1 x_1
n_2 x_2
...
n_T x_T
```

`x_i` 是预先确定的答案。整个文件只给 interactor 读取；选手仅收到 `T` 和当前组的 `n_i`。
这不改变题面中选手可见的输入格式。

| 选手发送 | interactor 的行为 |
| --- | --- |
| `? y`，`y < x` | 回复 `0` 并刷新 |
| `? y`，`y == x` | 回复 `1` 并刷新；选手仍需提交 `! y` |
| `? y`，`y > x` | 回复 `2` 并刷新 |
| `! y`，`y == x` | 本组结束；有下一组就发送下一组的 `n` |
| `! y`，`y != x` | WA，结束整个测试文件 |
| 第 101 次 `?` | WA，结束整个测试文件 |

`!` 后没有确认消息。最后一组结束后选手应立即退出，额外的非空白输出会被拒绝。
询问等号比较成功不会自动结束本组，仍然需要 `!`。
命令按空白分隔读取，选手按题面每行一条命令并刷新即可。

题面没有要求询问值必须落在 `[1,n]`，所以 interactor 允许有符号 64 位整数询问值，
仅比较大小；隐藏答案仍严格限制在 `[1,n]`。最终答案必须与隐藏答案相等。

请把已确认的回复含义（0 猜小、1 猜对、2 猜大）和 `sum(n) <= 10^9` 写入题面。

## 程序

- `gen.cpp`：生成隐藏数据，按总预算分配每组的 `n`。
- `val.cpp`：严格校验 `T`、`n`、`x`、空格、换行、EOF 和 `sum(n)`。
- `interactor.cpp`：回答询问，检查最终答案和每组查询上限，最终返回 testlib 的判定。
- `std.cpp`：选手视角的二分程序，每组最多 30 次查询，使用 `endl` 刷新。

无需 checker：interactor 已经完成本题的全部答案判定。
`linteractive` 在 interactor 返回 `_ok`，且选手正常退出、资源未超限时判 AC。
本题也不需要生成 `.ans`；空答案文件和空 `tout` 属于正常情况。

`setTestCase(tc)` 只标记当前组，便于报错定位。`T`、各组数据、切换逻辑都由程序显式处理。
它不会拆分测试文件或重置时间限制。每组查询次数由循环中的 `queries = 0` 重置。
这套代码不使用会重定向生成器输出的 `startTest()`。

## 命令行编译与验证

从本例目录编译生成器与输入校验器：

```bash
g++ -std=c++17 -O2 -I../../etc/ljudge/_default gen.cpp -o gen
g++ -std=c++17 -O2 -I../../etc/ljudge/_default val.cpp -o val
```

interactor 和选手由 linteractive 自动编译；在工程根目录调用：

```bash
./ljudge/src/linteractive \
  --etc-dir /etc/ljudge \
  --solution-code ljudge/examples/number-bomb/std.cpp \
  --user-code ljudge/examples/number-bomb/interactor.cpp \
  --max-cpu-time 2 --max-real-time 6 --max-memory 256m \
  --max-checker-cpu-time 5 --max-checker-real-time 8 \
  --testcase --input 1.in --output 1.out
```

其中 1.in 按上面的隐藏数据格式准备，1.out 为已有空文件。
所有 T 组共用一次进程运行的时间配额，题面上限的大量交互仍需在目标机器进行
压力测试并设置合适的交互器限制。独立回归测试已覆盖该例子的六组边界输入，
见根目录 TESTING.md。
