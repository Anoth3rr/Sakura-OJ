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
当前 Studio 在 interactor 返回 `_ok`，且选手正常退出、资源未超限时判 AC。
本题也不需要生成 `.ans`；空答案文件和空 `tout` 属于正常情况。

`setTestCase(tc)` 只标记当前组，便于报错定位。`T`、各组数据、切换逻辑都由程序显式处理。
它不会拆分测试文件或重置时间限制。每组查询次数由循环中的 `queries = 0` 重置。
这套代码不使用会重定向生成器输出的 `startTest()`。

## 生成参数

```text
gen T sumN mode seed
```

`T <= sumN <= 10^9`。`sumN` 是本文件所有 `n` 的总预算，不能当成每组 `n` 的上限参数。
`seed` 是显式种子；调用 `rnd.setSeed(seed)` 后，生成过程可复现，随机算法版本为 1。

| mode | n 的构造 | x 的构造 |
| --- | --- | --- |
| 0 | `rnd.partition(T, sumN)`，随机正整数拆分，总和恰为 sumN | `[1,n]` 内随机 |
| 1 | 尽量平均分配，总和恰为 sumN | `[1,n]` 内随机 |
| 2 | 尽量平均分配，总和恰为 sumN | 固定为 1 |
| 3 | 尽量平均分配，总和恰为 sumN | 固定为 n |
| 4 | 优先覆盖 1、2 的幂及其相邻值，逐组预留后续最小预算，总和不超过 sumN | 循环覆盖左端、右端、中点和随机值 |

`gen_params.txt` 是用于当前工作台试运行的 10 个测试点，覆盖单组 `n=10^9` 和多组交互。
`gen_stress_params.txt` 包含 `T=200000` 的压力数据，适合检查评测机是否能承受题面上界。
默认 10 个点未包含这种最大 T 的压力数据，不能据此认为整个约束范围均已通过当前评测机。

## 工作台填写方法

1. General Info 选择“交互”，设置时间和内存限制。
2. Tests 上传 `gen.cpp` 并填写 `gen_params.txt` 中的生成参数；Validator 上传 `val.cpp`。
3. Checker 上传 `interactor.cpp`，checker 留空。
4. Solution 上传 `std.cpp`，标记为 Main Correct；jury answer 生成程序留空。
5. 保存后在 Tests 生成并验证，再到 Invocations 运行标程或其他解法。

工作台自动提供 `testlib.h`。在本目录手工编译可使用：

```bash
g++ -std=c++17 -O2 -I../../vendor gen.cpp -o gen
g++ -std=c++17 -O2 -I../../vendor val.cpp -o val
g++ -std=c++17 -O2 -I../../vendor interactor.cpp -o interactor
g++ -std=c++17 -O2 std.cpp -o std
```

## 验证与资源限制

`verify.py` 使用临时目录调用 Studio Engine，检查回复含义、询问上限、跨组计数、非法命令、错误答案、EOF、未刷新和异常退出，并穷举小范围答案。

在项目根目录运行（需要已经安装的 newjudge 环境）：

```bash
sudo -u sakura /opt/sakura/venv/bin/python app/studio/examples/number-bomb/verify.py --full-scale
```

生成的 `verification.json` 是本地测试报告，不加入 Git。所有 T 组共享一次进程运行的时间配额；最大 T 的输入可能产生数百万次逐次交互，需要在目标机器上重新评估选手和交互器的时间预算。工作台固定的交互器 CPU 限制不会随选手限制一起改变，应在使用完整压力数据发布前检查结果。
