# 两步调用：先编译，再判题

文件 A 是 `script/compile-communication.sh`。它只准备沙箱、编译选手源码和
裁判、生成 JSON 请求清单，执行到这里即退出。它不运行选手、
interactor、checker、validator 或 lworkflow，也不启动 Web 服务。Bash 文件内包含这一段编译逻辑，
通过 Python 标准库调用独立的 `lib/newjudge/compiler.py`、`languages.py` 和 `source.py`。

支持两种接口，按裁判程序的协议选择：

| 裁判参数 | 流程 |
| --- | --- |
| `--validator-code validator.cpp` | DOMjudge 标准多轮：运行选手，validator 检查并决定是否生成 nextpass.in |
| `--interactor-code interactor.cpp --checker-code checker.cpp` | testlib 两轮通信兼容：首轮交互，tout 作为第二轮输入，checker 检查第二轮输出 |

这两组参数互斥。不能把普通 testlib checker 直接作为 DOMjudge validator。

## 已有 main.cpp、interactor.cpp、checker.cpp

在包含这三个源码、`1.in`、`1.out` 的目录，以非 root 判题账户执行：

```bash
bash /path/to/newjudge/script/compile-communication.sh \
  --user-code main.cpp \
  --interactor-code interactor.cpp \
  --checker-code checker.cpp \
  --max-cpu-time 2 --max-real-time 6 --max-memory 512m --max-output 8m \
  --testcase --input 1.in --output 1.out \
  --request-dir ./requests > compile-result.json
```

确认编译命令退出码为 0，再独立调用：

```bash
/path/to/newjudge/ljudge/src/lworkflow \
  --request ./requests/001.request.json \
  --output ./1.actual > workflow-result.json
```

`lworkflow` 自动执行完整两轮流程，调用方不需要手动启动 interactor 或 checker：

1. 首轮 main 与 interactor 通过标准输入输出通信。
2. interactor 的 `tout` 文件作为第二轮 main 的标准输入；启动全新的选手进程和工作目录。
3. checker 接收原始 `1.in`、第二轮选手输出和 `1.out`，给出最终结果。

interactor 和 checker 使用官方 testlib 参数及 0/1/2 退出码。
`--max-*` 限制分别应用于两次选手运行；`--max-interactor-*` 和
`--max-checker-*` 分别限制两份裁判。编译只进行一次，判题不需要 Python 服务。
`--validation-passes` 在此兼容模式中只能为 2。`1.out` 可以是已有的空文件，
前提是该题的裁判不读取标准答案。源码的具体协议见 [WORKFLOWS.md](WORKFLOWS.md)。

## 文件 A：DOMjudge 多轮编译和生成清单

在包/仓库根目录，以已经配置好 lrun 的非 root 判题账户执行：

```bash
bash script/compile-communication.sh \
  --etc-dir /etc/ljudge \
  --user-code main.cpp \
  --validator-code validator.cpp \
  --validation-passes 2 \
  --max-cpu-time 2 --max-real-time 6 --max-memory 512m \
  --testcase --input 1.in --output 1.out \
  --testcase --input 2.in --output 2.out \
  --request-dir ./requests \
  > compile-result.json
```

成功后生成 `requests/001.request.json`、`requests/002.request.json`。
stdout 是编译报告，`success: true`、`status: PREPARED` 表示编译及清单准备
成功，尚未进行判题。报告还包含编译产物和每个清单的绝对路径。

`--request-dir` 必须指定尚不存在的新目录。源码、输入和答案路径相对当前
调用目录；脚本可以使用绝对路径从其他目录调用。输入和答案按各自出现顺序
一一配对；`--output` 是标准答案，若不使用答案仍需传入已有空文件。

编译退出码为 0 才可以进行下一步；源码/validator 编译失败或环境故障返回
1，参数错误返回 2。编译产物默认缓存于当前账户的 `~/.cache/lcommunication`，
也可通过 `--cache-dir` 指定。后续判题前必须保留该缓存和测试数据。

## lworkflow：独立执行判题

执行器只需首次构建或更新源码时重新构建：

```bash
make -C ljudge/src lworkflow
```

文件 A 不依赖 lworkflow 二进制已经存在，可以先编译题目，再准备执行器。
由调用方在文件 A 成功之后执行：

```bash
./ljudge/src/lworkflow \
  --request ./requests/001.request.json \
  --output ./001.actual \
  > ./001.result.json

./ljudge/src/lworkflow \
  --request ./requests/002.request.json \
  --output ./002.actual \
  > ./002.result.json
```

这里的 `--output` 是选手最后一轮的实际输出。stdout 为单个测试点的 JSON
判题结果，读取其中的 `verdict` 判断 AC/WA/TLE 等。一次 lworkflow 调用执行
一个测试点的完整多轮流程，不需要调用方逐轮启动程序。

两步必须在同一台评测机、同一评测账户下执行；清单引用本机绝对路径。

## 包内例子

```bash
bash script/compile-communication.sh \
  --user-code ljudge/examples/communication/main.cpp \
  --validator-code ljudge/examples/communication/validator.cpp \
  --testcase -i ljudge/examples/communication/1.in -o ljudge/examples/communication/1.out \
  --testcase -i ljudge/examples/communication/2.in -o ljudge/examples/communication/2.out \
  --request-dir ./requests
```

然后单独使用上一节的 lworkflow 命令。两点应分别 AC、`passes: 2`，实际输出
为 `6\n` 和 `42\n`。选手可换成同目录的 `main.py3`。

## 环境和参数

需要 Bash、Python 3.10+、各语言工具链，以及本项目已配置好的 lrun、
lrun-mirrorfs 和 cgroup v1。默认运行环境为项目根目录下的 `runtime/`，
其中包含 `bin/lrun`、`bin/lrun-mirrorfs`、`mirrorfs.conf`、`testlib.h`。
脚本不负责部署运行环境或重启服务。

| 参数 | 说明 / 默认值 |
| --- | --- |
| `--language` / `--validator-language` | 显式语言配置名，否则按原生 ljudge 源码后缀选择 |
| `--interactor-language` / `--checker-language` | testlib 兼容入口的裁判语言配置名 |
| `--etc-dir` | 语言配置目录，默认 `/etc/ljudge` |
| `--runtime` / `--testlib` | 运行环境根目录 / testlib 头文件 |
| `--cache-dir` | 编译缓存和临时工作根目录 |
| `--validation-passes` | 运行轮数上限，默认 2，范围 1～32 |
| `--max-cpu-time` / `--max-real-time` | 写入清单的选手每轮 CPU / wall 秒数，默认 2 / 6 |
| `--max-memory` / `--max-output` | 选手每轮内存 / 输出限制，默认 512m / 8m |
| `--max-validator-cpu-time` / `--max-validator-real-time` | validator 每轮 CPU / wall 秒数，默认 5 / 8 |
| `--max-validator-memory` / `--max-validator-output` | validator 每轮内存 / 输出限制，默认 512m / 8m |
| `--max-interactor-cpu-time` / `--max-interactor-real-time` | 首轮 interactor 的 CPU / wall 秒数，默认 5 / 8 |
| `--max-interactor-memory` / `--max-interactor-output` | interactor 内存 / 输出限制，默认 512m / 8m |
| `--max-checker-cpu-time` / `--max-checker-real-time` | 第二轮 checker 的 CPU / wall 秒数，默认 5 / 8 |
| `--max-checker-memory` / `--max-checker-output` | checker 内存 / 输出限制，默认 512m / 8m |

所有限制作用于该清单内对应角色的每次运行；编译仍使用 Compiler 的编译限制。
内存/输出支持整数字节数和 k/m/g 后缀；输出限制最大 64m。JVM 堆上限使用
对应角色的内存限制。`.py` 选择原生 `py` 配置，`.py3` 选择 `py3`；可用
`--language py3` 显式覆盖文件后缀。

`--validator-code` 使用 DOMjudge 的 42/43 和 `feedbackdir/nextpass.in` 协议，详见
[WORKFLOWS.md](WORKFLOWS.md)。查看编译入口参数：

```bash
bash script/compile-communication.sh --help
```

首次准备运行目录：`python3 script/setup-runtime.py`。它复用 PATH 中已配置好的
`lrun` / `lrun-mirrorfs`，不需要 Web 服务。可用 `NEWJUDGE_RUNTIME` 或 `--runtime` 指定其他目录。
