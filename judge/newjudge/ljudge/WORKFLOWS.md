# 原生交互与多阶段判题

`lworkflow` 是独立的 C++17 命令行执行器。它借鉴 DOMjudge 将语言启动、
进程通信和沙箱分开的实现方式，并实现 DOMjudge 的多阶段 output validator
协议。此实现由本项目独立编写，沙箱继续使用 `lrun`。

```text
compile-communication.sh / 任务队列
  → 读取 ljudge 语言配置，编译程序，生成运行清单
  → lworkflow（C++：管道、进程生命周期、阶段切换、结果汇总）
      → lrun → 选手程序
      → lrun → interactor / checker / output validator
```

独立模块 `lib/newjudge/compiler.py` 负责语言配置、编译和生成清单。交互管道、通信内容转交、
多阶段循环、超时监督和临时目录清理由原生执行器负责。已生成的运行清单
可以直接交给命令行，不需要 Python 服务参与执行。

## 编译与调用

已有源码时，先调用 `bash script/compile-communication.sh` 编译并生成清单，
再由调用方独立调用 `lworkflow` 判题。编译入口支持 `--user-code`、
`--validator-code`（或 `--interactor-code` + `--checker-code`）、
多组 `--testcase --input --output` 和 `--request-dir`。
完整示例见 [COMPILE_COMMUNICATION.md](COMPILE_COMMUNICATION.md)。
下面是底层执行器的调用方式。

在 Linux 上使用支持 C++17 / `std::filesystem` 的编译器：

```sh
make -C ljudge/src lworkflow
ljudge/src/lworkflow --help
ljudge/src/lworkflow --request manifest.json --output result.bin
```

正常结束时 stdout 返回一份 JSON 报告，退出码为 0；选手 WA/TLE/RE 等属于
正常评测结果。沙箱启动、状态报告或文件协议错误时，退出非 0，stderr 描述
故障，调用者应标记 IE。选手最后一轮输出或交互记录写入 `result.bin`。

以专用非 root 评测账户运行；`lworkflow` 本身不需要 setuid。它依赖已经安装
的 `lrun`、镜像与 cgroup 环境。独立包使用 `script/setup-runtime.py` 准备本地
运行目录，由调用方直接执行 `ljudge/src/lworkflow`，见 [README](../README.md)。

## 多阶段通信协议

运行清单使用 `mode: multipass` 和 `validation_passes`。
后者为最多运行轮数，取值 1～32，并不要求每次恰好运行这么多轮。

每轮运行同一份选手程序，stdin 为本轮输入，stdout 被完整捕获。随后启动
output validator：

```text
validator input answer feedbackdir
```

选手本轮输出是 validator 的 stdin。`input` 是本轮输入文件，`answer` 是
该测试点的 jury answer，两者只读。`feedbackdir` 是可写的私有反馈目录。

| validator 结果 | 执行器行为 |
| --- | --- |
| 正常退出 42，没有 `feedbackdir/nextpass.in` | 整个测试点 AC |
| 正常退出 42，存在 `feedbackdir/nextpass.in` | 将其作为下一轮 stdin，启动新的选手进程 |
| 正常退出 43，没有 `nextpass.in` | WA |
| 其他退出码、崩溃或资源超限 | IE |
| 退出不是 42 却生成 `nextpass.in` | IE |
| 已达到轮数上限却继续请求下一轮 | IE |

`nextpass.in` 被消费后删除，其他反馈文件跨轮保留。空的 `nextpass.in` 仍表示
请求下一轮，下一轮输入为空。选手不能访问反馈目录、jury answer 或其他轮的
工作目录；每轮均复制完整编译产物到新目录，文件修改不会污染缓存。

每轮 validator 的工作目录也重新创建，跨轮状态应写入 `feedbackdir`。
`judgemessage.txt` 用于 AC/WA 说明，validator 异常时读取 `judgeerror.txt`
作为诊断；两者最多读取 16 KiB。反馈目录只允许普通文件和目录，最多 4096
项 / 16 MiB；下一轮输入最多 8 MiB，不接受符号链接、FIFO 或其他特殊文件。

选手每轮独立应用时间、内存和输出限制。报告汇总选手 CPU 时间之和、峰值
内存的最大值，包含 `passes` 与逐轮 `phases`。`message_bytes` 表示已传递的
`nextpass.in` 累计字节数；题目定义的消息长度和编码约束由 validator 检查。
编译入口默认给 output validator 5 秒 CPU、8 秒 wall、512 MiB 内存限制，
可通过 `--max-validator-*` 参数调整。

不能直接使用返回 0/1/2 的 testlib checker 作为 output validator，必须遵守
上述参数和 42/43 协议。编译入口的 `--output` 可接收调用者已有的非空
answer 文件；不使用答案时仍需传入已有空文件。

完整的两轮短消息示例位于 `examples/communication/`。
示例 validator 校验 Sender 输出、写入私有期望值和下一轮输入，再校验
Receiver 输出；两轮由 stdin 中的 `send` / `receive` 标记区分。

## testlib 两轮通信兼容

`communication` 模式支持已有 `main`、`interactor`、`checker` 的题目：

```text
原始 input → interactor ⇄ main（第一次，双向标准流）
                   ↓ tout
              下一轮输入 → main（第二次，全新进程与工作目录）
                                ↓ stdout
原始 input + 原始 answer ─────→ checker → 最终判定
```

interactor 的调用方式为 `interactor input transcript answer`，使用
`registerInteraction`；`tout` 写入 transcript。第一轮选手正常结束且 interactor
正常返回 0，才会启动第二轮。第二轮使用同一份编译产物的全新副本，不能访问
第一轮工作文件、隐藏输入、标准答案或裁判。没有 transcript 文件视为故障，
已有空文件则是合法的空输入，最多允许 8 MiB。

第二轮正常结束后执行 `checker input output answer`，使用 `registerTestlibCmd`。
三个文件均只读，分别是原始隐藏输入、第二轮实际输出和原始标准答案。
checker 返回 0/1/2 对应 AC/WA/PE；崩溃、超限及其他退出码为 IE。
选手自身的 RE/TLE/MLE/OLE 会阻止后续检查，不能被裁判的 AC 覆盖。

执行器独立限制每次选手运行，报告汇总 CPU/wall 时间之和与最大峰值内存；
`passes` 为已执行的选手轮数（1 或 2），`phases` 保留每轮结果以及裁判报告，
`message_bytes` 为 interactor 生成的下一轮输入字节数。
`--output` 保存第二轮实际输出；首轮失败时为空。编译入口仍只准备清单。

这是 newjudge 对 testlib 题包的兼容入口，借鉴 DOMjudge 的独立执行、
裁判分离和逐轮启动方式；不是 DOMjudge 标准题包协议。DOMjudge 文档明确规定
其标准 multi-pass 不能与 interactive 类型混用。使用标准 DOMjudge validator
时仍选择上面的 `multipass` 模式，采用 42/43 与 `nextpass.in`。

真实沙箱回归：以非 root 评测账户执行
`python3 tests/test_communication.py --runtime /path/to/runtime --report /path/to/report.json`。
覆盖完整 testlib 流程、两轮隔离、隐藏文件隔离、只读 checker 数据、WA/PE/RE、
CPU/内存/输出超限、裁判错误/超时、缺失/FIFO/空 transcript、Bash 流式启动和编译失败。

## 交互与旧通信题

`interactive` 模式在两个 lrun 沙箱间连接两条管道。保留已有 testlib
`interactor input transcript answer` 协议，0/1/2 对应通过/WA/PE。选手程序
自身的 RE/TLE/MLE 等不能因为 interactor 接受而被忽略。调用方可以在交互
结束后另行检查 transcript；原生 `linteractive` CLI 继续可用。

`run-twice` 模式兼容 `send-receive-stdin-v1`：通过 argv/JUDGE_PHASE 区分
阶段，第一轮 stdout 原样作为第二轮 stdin，消息超限 CLE。
编译脚本根据裁判参数生成 `multipass` 或 `communication` 清单；
`interactive`、`run-twice` 由调用方自行提供对应清单。

## 运行清单

清单是**可信调度器接口**，不应直接接收参赛者提交的命令或宿主路径。
语言解析及路径/命令生成可复用 `Compiler.native_program`；可执行例子见
`tests/test_compile_communication.py` 的两步调用检查。

| 顶层字段 | 含义 |
| --- | --- |
| `version` | 固定为 1 |
| `mode` | `interactive`、`communication`、`multipass` 或 `run-twice` |
| `work_root` | 专用评测账户可写的宿主临时目录 |
| `input` / `answer` | 输入及 jury answer 的绝对路径 |
| `program` | 选手 ProgramSpec |
| `interactor` | interactive / communication 模式的 ProgramSpec |
| `checker` | communication 模式第二轮 checker 的 ProgramSpec |
| `validator` / `validation_passes` | multipass 模式的 ProgramSpec 及轮数上限 |
| `receiver` / `message_bytes` | run-twice 模式的 ProgramSpec 及消息上限 |

ProgramSpec 包含 `artifacts`（完整编译产物目录）、`command`（lrun 的完整
argv 数组，必须将沙箱状态写入 fd 3）、`wall_limit`、`output_limit`。
`files` 声明需要建立的 input/answer/output 挂载点，`directories` 声明
feedback 目录挂载点，实际挂载规则由 argv 指定。

argv 支持 `@WORK@`、`@INPUT@`、`@ANSWER@`、`@OUTPUT@`（供后置 checker）、`@FEEDBACK@`、`@PHASE@`、
`@PASS@` 占位符。逐参数替换后直接 exec，不做 shell 求值。编译产物只允许
普通文件和目录，最多 64 MiB / 4096 项。内部状态文件不挂入选手沙箱。

## 参考及边界

参考 [DOMjudge 开发版多阶段协议](https://www.domjudge.org/snapshot/manual/config-advanced.html)、
[judgedaemon](https://github.com/DOMjudge/domjudge/blob/main/judge/judgedaemon.main.php)
与 [runpipe](https://github.com/DOMjudge/domjudge/blob/main/judge/runpipe.cc)。
这里复用其协议和职责划分，没有引入 PHP daemon 或替换为 runguard，也不是
完整的 DOMjudge 题包导入器。多阶段和双向交互是独立模式。

语言仍由原生 ljudge 配置决定；执行器不按语言增加分支。所需工具链、运行库
和流式启动命令必须在评测机可用。已验证范围见根目录 `TESTING.md`。
