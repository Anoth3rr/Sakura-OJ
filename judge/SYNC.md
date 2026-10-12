# newjudge 集成说明

`newjudge/` 收录 Sakura 使用的评测机源码。此仓库不依赖维护者的个人源码目录，也不包含部署缓存、编译产物或数据库快照。

支持原生 testlib 两轮通信、独立通信编译入口与输出量统计。Sakura 提供 `testlib-communication-v1`、`send-receive-stdin-v1` 和 `domjudge-multipass-v1` 三种通信协议，录题、生成、发布快照和 OJ 提交使用对应配置。

## 集成补丁

- `lrun/src/lrun.cc`：RLIMIT_CPU 比题目 CPU 限制延后 1 秒作为备用；cgroup 继续执行原限制。新上游的输出统计实现已替换旧的本地 fstat 补丁。
- `lrun/src/options/parse.cc`：文件大小硬限制多留一个溢出标记字节，用于识别解释器捕获 SIGXFSZ 后退出的 OLE。
- `lrun/utils/mirrorfs/mirrorfs.cc`：镜像初始化使用 umask 0022，兼容服务 UMask=0077。
- `ljudge/src/{ljudge,linteractive}.cc`：未显式设置 Java 堆上限时回退到题目内存限制。
- `lib/newjudge/compiler.py`：复用 Sakura 的 Java 21 镜像内容及镜像创建权限，独立编译入口可直接使用 `/opt/sakura/runtime`。

同步上游时需要合并这些差异。`scripts/install_wsl.py` 从当前源码重建五个原生程序，并生成 C、C++、Python、PyPy、Java 配置。遗留语言配置中的路径已改为通用示例；不支持直接复用它们替代安装脚本。涉及旧站点的 MySQL/Oracle 连接配置不包含在公开仓库中。

## 独立编译与执行

在 WSL 中以 `sakura` 账户执行以下两个步骤。`--request-dir` 须为尚不存在的目录；文件路径需对该账户可读。编译阶段只生成程序和执行清单，不进行判题。

```bash
bash judge/newjudge/script/compile-communication.sh \
  --runtime /opt/sakura/runtime \
  --etc-dir /opt/sakura/runtime/etc/ljudge \
  --cache-dir /var/lib/sakura/judge/native/communication \
  --request-dir /tmp/communication-requests \
  --user-code /data/main.cpp \
  --interactor-code /data/interactor.cpp \
  --checker-code /data/checker.cpp \
  --testcase --input /data/1.in --output /data/1.ans

/opt/sakura/runtime/bin/lworkflow \
  --request /tmp/communication-requests/001.request.json \
  --output /tmp/communication-result.out
```

DOMjudge 多阶段模式则使用 `--validator-code` 和 `--validation-passes`，不能同时传入 interactor/checker。完整参数说明见 [通信编译入口](newjudge/ljudge/COMPILE_COMMUNICATION.md)。
