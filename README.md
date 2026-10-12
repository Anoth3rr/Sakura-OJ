# Sakura OJ

Sakura 将 **Online Judge、集训队管理、testlib 录题工作台和 newjudge 评测机**整合为一个 FastAPI 服务和一套账号权限。

- OJ：题库、Markdown/公式题面、多语言提交、评测记录、题库和账号管理。
- 录题工作台：Polygon 式分区、生成器/校验器/检查器、交互器、试卷管理、多解法及批量 Invocations。
- 评测：普通题、交互题、run-twice / testlib 两轮 / 多阶段通信题，支持 C、C++、Python、PyPy 和 Java。
- 集训队：成员档案、平台账号与牛客 UID、Rating、比赛、提交同步和分析。

仓库只包含源码、公开依赖、合成测试和示例，不包含实际账号、成员资料、提交记录、隐藏题库或部署配置。发布维护说明见 [PUBLICATION.md](PUBLICATION.md)。

## 安装与启动

推荐使用 Ubuntu 24.04 或具有 systemd 的 WSL2 发行版。newjudge 需要 **cgroup v1 memory 控制器**：

```bash
test -f /sys/fs/cgroup/memory/memory.limit_in_bytes
```

如果检查失败，需要先配置支持 memory cgroup v1 的内核和挂载；只安装用户态工具无法补出内核支持。内核配置应包含 `CONFIG_CGROUPS=y`、`CONFIG_MEMCG=y`，启动参数不能禁用 v1 memory。本仓库不包含本机内核镜像或 WSL 配置。

```bash
git clone https://github.com/Anoth3rr/Sakura-OJ.git
cd Sakura-OJ
sudo apt-get update
sudo apt-get install -y build-essential rake pkg-config libseccomp-dev python3-venv pypy3 openjdk-21-jdk-headless
sudo python3 scripts/install_wsl.py
```

安装脚本编译 lrun、lrun-mirrorfs、ljudge、linteractive、lworkflow，创建专用 `sakura` 服务账号，并安装 systemd 服务。项目目录须能被该账号读取和遍历；首次安装会为该账号创建可写的 `data/` 和 `runtime/`。默认只监听 `127.0.0.1:8000`，使用一个应用进程。

首次安装会在仓库外的 `/etc/sakura.env` 生成独立管理员密码，文件仅 root 可读。使用 `sudoedit /etc/sakura.env` 查看或在首次启动前配置管理员账号；不要将这个文件复制进 Git。已有配置文件不会被覆盖，已有账号密码不会因环境变量变化而重置。若自行配置新的环境，必须设置 `OJ_ADMIN_PASSWORD`，不提供通用默认密码。

```bash
sudo systemctl restart sakura
sudo systemctl status sakura
journalctl -u sakura -f
```

Windows 下可在项目目录运行：

```powershell
.un.ps1 -Install              # 首次安装，需先完成内核和依赖配置
.un.ps1                       # 启动已安装的服务
.un.ps1 -Restart -OpenBrowser # 重启并打开页面
.un.ps1 -Quiet                # 保持 WSL 会话，不持续输出日志
```

脚本默认发行版为 `Ubuntu-24.04`，可用 `-Distro` 修改。路径根据脚本所在目录计算。保留启动终端可避免 WSL 空闲退出；关闭终端不主动停止 systemd 服务。必要时可为当前 PowerShell 进程设置 `Set-ExecutionPolicy -Scope Process Bypass`。

| 入口 | 地址 | 权限 |
| --- | --- | --- |
| OJ 题库、题面、提交 | http://localhost:8000/ | 公开浏览，登录后提交 |
| 录题、组卷、生成数据、Invocations、发布 | http://localhost:8000/studio/ | 管理员 / 题目管理员 |
| 集训队档案、Rating、比赛、分析 | http://localhost:8000/team/ | 管理员 / 老师 |
| OpenAPI | http://localhost:8000/docs | 各 API 仍按角色鉴权 |
| 健康检查 | http://localhost:8000/health | `judge.ready` 表示沙箱是否可用 |

学生只能查看自己的提交详情；老师和管理员可查看提交进行复盘。模块间共享登录状态。

配置变量见 [.env.example](.env.example)。应用不自动加载根目录的 `.env`；systemd 使用 `/etc/sakura.env`，手动启动时通过进程环境传入配置。集训队示例成员默认关闭。

`run-local.ps1` 用于本机开发，关闭鉴权并直接运行代码，不提供 newjudge 隔离；只使用可信测试程序。`run-docker.ps1` 是普通题的备用后端，首次使用同样需要自行设置管理员密码。交互题和通信题使用 newjudge。

## 录题到学生提交

1. 在“录题工作台”的题目列表创建或选择题目。创建时分配唯一的四位题目 ID（如 `0001`），仅在列表中显示；在 **General Info** 设置名称、判题方式、通信协议和资源限制，在 **Statement** 编辑 Markdown 题面并预览公式。
2. 在 **Checker** 上传或编辑答案检查器；交互题在同页配置 `interactor`，checker 可选；多阶段通信题配置输出验证器。在 **Validator** 配置 testlib 输入校验器。在 **Solution** 上传多份解法，并指定一份 **Main Correct** 作为标程。
3. 在 **Tests** 配置数据生成器，每行填写一组生成参数，点击“生成并验证”。每行生成一个测试文件；文件内多组数据由题目定义。此页可查看输入、答案、校验结果和生成日志。
4. 在 **Solution** 为其他解法标记 Correct、Wrong、Time Limit、Memory Limit 等预期结果并保存；在 **Invocations** 勾选部分解法或运行全部，查看「解法 × 测试点」结果矩阵、耗时、内存、详情及是否符合预期。临时代码试运行仍可使用，默认留空，暂存于当前浏览器。
5. 在 OJ 首页“管理题库”中填写或选择题目 ID，点击“添加到题库”；也可直接在录题工作台点击“发布到 OJ”。新题的 slug 自动由编号生成，已有链接保持原样。题面、评测程序、限制与数据保存为发布快照；生成的数据默认全部隐藏，公开样例请写入题面。
6. 学生在题库选择题目并提交，后台调用共享 lrun 沙箱，展示分数、耗时、内存和通信量。

修改草稿不改变已发布题目。更新评测配置后需重新生成数据并再次发布。新发布保留历史提交和旧测试点；排队中的提交使用提交时的配置与数据。

草稿可移入回收站并恢复；删除草稿不会自动撤回已发布 OJ 题目。录题统一通过录题工作台完成，旧 ZIP 导入入口及上传接口已移除。

工作台按 General Info、Statement、Checker、Validator、Tests、Solution、Invocations 七个分区组织，生成历史和评测历史分别归入 Tests 与 Invocations。旧分区链接 `config`、`data`、`run` 会分别跳转到 General Info、Tests、Invocations。

### 试卷与多解法

侧栏进入“试卷管理”，新建试卷后填写名称和 Markdown 说明，按四位题目 ID 添加，或从下拉列表选择题目。支持调整题序、移除题目、预览整卷和导出 ZIP。试卷保存的是有序题目引用，预览和导出读取当前已保存的题面与材料；同一题可以被不同试卷引用，同一卷内不可重复。删除试卷或移出卷内题目不删除原题。已移入回收站的题目会标注状态，恢复或移除后才能保存和导出整卷。

每题最多保存 32 份解法，单份源码不超过 512 KiB，全部解法（含独立 Receiver）合计不超过 4 MiB。支持批量上传、编辑、移除与修改语言。`.py` 可选 CPython / PyPy，Java 入口为 Main 类。每题至多一份 `main-correct`；选中新的 Main Correct 时，原标程改为 Correct。已经添加解法的题目在生成数据前必须指定 Main Correct。旧版题目的参考标程继续兼容，普通 / run-twice / 多阶段题可一键迁移到解法列表。

普通题 Main Correct 生成 `.ans`，run-twice 使用两个阶段的最终输出生成 `.ans`，多阶段执行完整流程自检。交互题和 testlib 两轮通信题的 Main Correct 是完整选手程序，生成数据时通过交互器 / checker 自检；需要 jury answer 时，另在 Solution 配置可选的普通输入输出答案生成程序。Main Correct 自检失败时新数据不会启用。

| 标记 | 预期结果 |
| --- | --- |
| Main Correct / Correct | 所有测试点 AC |
| Wrong | 至少一个测试点 WA 或 PE |
| Time Limit / Memory Limit | 至少一个测试点 TLE / MLE |
| Runtime Error / Output Limit | 至少一个测试点 RE / OLE |
| Communication Limit / Compile Error | 至少一次 CLE / CE |

任何 IE 均不算符合预期。批量任务会运行全部测试点，保存选中的解法 ID、名称、语言、标签、源码 SHA-256、题目版本、数据集 ID 和逐点结果；后续编辑不改变已有结果。`MATCH` 表示全部所选解法符合标记，`MISMATCH` 表示至少一份不符，不等同于全部解法 AC。修改非 Main Correct 解法不使测试数据失效；修改 Main Correct 源码或评测配置则需要重新生成。

题包导出格式升级为 `sakura-studio-v2`，`solutions/` 保存每份解法，`problem.json` 保存标签、语言和文件路径。整卷导出包含 `paper.json`、合并题面 `statement.md`，以及按顺序和题目 ID 命名的题目子目录；当前有效测试数据随题导出，草稿题的数据未就绪时仅导出题面和程序。

### 题库和账号管理

首页题库以表格列表展示题目 ID、标题、题型、难度、提交次数、通过率和操作，支持搜索、难度筛选及分页。默认不打开任何题面；点击标题或“预览”进入完整题面和代码提交页，通过“返回题库列表”或浏览器后退回到列表。

题目编号以四位数字显示（如 `0001`、`0010`），在题库、管理题库和工作台列表中作为标识。具体题面、信息栏和浏览器标题不展示编号。题目详情采用宽幅正文与右侧信息栏布局，顶部显示标题、提交/通过次数及时间、内存限制。题目描述、输入输出格式和样例连续展示，右侧目录可跳转至相应章节；“提交代码”和“提交记录”使用独立页签。公开样例提供输入、输出复制按钮；工作台 Markdown 中的 `text input:#1` / `text output:#1` 样例代码块也按同一布局展示。完整 Markdown 已含输入输出章节时，不重复追加旧字段。

“提交代码”默认空白，不再预填示例解法。可在语言选择框旁打开“代码模板”，编写或从当前代码复制个人模板；留空保存可取消该语言的模板。模板按账号和语言保存在当前浏览器，刷新后仍可用于新题目，不跨浏览器或设备同步。当前页面内，各题目、各语言的代码分别暂存，切换语言或返回题目时恢复；保存模板不会覆盖正在编写的代码。代码草稿仅保留至刷新，模板长期保存，退出账号后不会向其他账号显示原账号的模板或草稿。

管理员和题目管理员可使用独立的“管理题库”列表页：按题目 ID / 标题和状态筛选，通过“添加到题库”填写或选择 ID。所有 OJ 题目均关联录题草稿，“编辑”进入完整题面、评测配置和测试数据。启动服务或加载管理列表时，系统会为缺少草稿的旧题补建关联；包括已移出公开题库的题目。已有草稿和回收站状态不会被覆盖，回收站草稿可单独恢复。编号在创建时分配，编辑、发布、移出题库或恢复都不改变编号；已发布草稿与对应 OJ 题目共用一个 ID。题包导出也包含 `problem_code`。

旧题首次接入工作台时复制原有输入、答案和公开样例，不修改在线题目、测试点或历史提交。管理员可以直接编辑题面和资源限制、试运行和重新发布；发布沿用原题 ID、链接、难度及测试点权重/样例可见性。旧普通题未上传 checker 时，试运行和 OJ 均使用原有文本比较规则。原有数据标注为“原有数据”，不宣称已通过 val；重新生成数据时仍需上传完整 testlib 工具。修改生成参数、程序或判题模式后须重新生成并验证；新建的工作台题目也须完成生成验证后才能发布。

题库中的“删除”表示移出公开题库：公开详情和新提交返回 404，已排队的提交、历史结果、发布数据和录题草稿保留。再次按原 ID 添加时恢复最近一次发布的快照；若要更新题面或评测数据，请在工作台重新发布。

管理员可在“账号”中创建或删除 OJ 账号。删除采用注销记录，立即撤销全部会话并移除密码，账号不再出现在列表，也不能登录、重新启用或使用同一用户名重新注册；历史提交的归属和数据保留，集训队档案独立保留。不能删除当前登录账号，数据库事务保证至少保留一个启用中的管理员。

管理 API（均检查角色和同源写入）：

- `GET /api/problem-bank?search=0001`：查询题目编号、是否已在题库及是否可添加。
- `POST /api/problem-bank`，`{"problem_code":"0001"}`：按编号添加，重复添加不会复制题目或测试点。
- `DELETE /api/problem-bank/0001`：移出题库。
- `DELETE /api/users/{user_id}`：注销 OJ 账号，仅管理员可调用。

### 三种判题方式

| 模式 | 执行方式 |
| --- | --- |
| 普通 `normal` | 每个测试文件运行选手程序，checker 比较输出 |
| 交互 `interactive` | 选手与 interactor 同时运行，双向连接 stdin/stdout |
| 通信 `communication` | 可选 run-twice 的 `send` / `receive` 两次执行，或由输出验证器控制的多阶段执行 |

gen 使用 `registerGen(argc, argv, 1)`，val 使用 `registerValidation(argc, argv)`，checker 使用 `registerTestlibCmd(argc, argv)`。interactor 直接使用标准 `registerInteraction(argc, argv)`，不需自行改写注册函数。

交互器收到 testlib 参数 `input transcript answer`：`inf` 读取隐藏输入，`ouf` 读取选手输出，`cout` 向选手发送消息，`tout` 写交互记录，`ans` 读取可选参考答案。

交互题允许不上传 checker：interactor `_ok`、选手正常退出且未超限后判 AC。上传 checker 时，在交互成功后对 `tout` 记录执行额外检查。参考答案可留空；如果程序需要读取 `ans`，须提供生成参考答案的普通程序。交互式选手标程在 Solution 的解法列表中标记为 Main Correct，再到 Invocations 评测。

通信题阶段参数：C/C++ 使用 `argv[1]`，Python/PyPy 使用 `sys.argv[1]`，Java 使用 `main(String[] args)` 的 `args[0]`。五种语言均可读取环境变量 `JUDGE_PHASE`。

通信题 Sender 读取完整输入，将消息写到 stdout；Receiver 的 stdin **只有消息**。两次执行不共享工作目录和内存。消息包含空格、换行，按字节计数，超限判 `COMMUNICATION_LIMIT_EXCEEDED`。时间和内存限制分别作用于两个阶段。工作台试运行还支持独立 Receiver；公开 OJ 使用一个程序运行两次的协议。

通信题还可在 General Info 中选择 **testlib 两轮 · interactor → 第二轮 → checker**（`testlib-communication-v1`）。首轮 interactor 使用 `registerInteraction(argc, argv)` 与选手双向通信，将下一轮输入写入 `tout`；首轮成功后，同一份选手程序在全新沙箱中启动，stdin 为 `tout` 内容。第二轮输出由 checker 使用 `registerTestlibCmd(argc, argv)` 检查，三个参数仍为原始 input、第二轮 output、原始 answer。每轮分别执行时间、内存和输出限制；消息格式与信息量限制由 interactor 校验，transcript 必须存在、可为空，最多 8 MiB。此协议不使用独立 Receiver，也不会自动传递 send/receive 参数，阶段标记由题目输入协议定义。

testlib 两轮通信的 interactor 和 checker 均必需。答案生成程序可选，按普通输入输出生成 jury answer；不上传则 answer 为空，checker/interactor 应自行判断正确性。完整两轮选手解法放在 Solution 的解法列表中，标程标记为 Main Correct，通过 Invocations 验证。通信协议旁的“创建当前协议示例”可创建配套 testlib 程序；切换协议会使已有数据失效，必须重新生成再发布。

通信题可在 General Info 的通信协议中选择 `domjudge-multipass-v1`，在 Checker 配置输出验证器。每轮执行同一程序，由输入中的内容区分阶段；输出验证器按 `validator input answer feedback_dir` 调用，从 stdin 读取选手输出，正常返回 42 表示通过、43 表示 WA，其他退出码或资源超限表示评测错误。通过后写入 `feedback_dir/nextpass.in` 进入下一轮，否则结束；轮数上限为 1～32，超限仍请求继续判评测错误。该验证器与普通 testlib checker 的注册方式不同。通信量由输出验证器检查，answer 文件为空；参考标程用于完整流程自检，可不上传。可从通信协议设置创建可直接运行的多阶段示例。

缺少 `communication_protocol` 字段的旧通信题继续按 `send-receive-stdin-v1` 执行，原有数据指纹保持兼容。协议及最大轮数随导出题包、发布快照保存；改成多阶段协议或修改其轮数后需要重新生成数据。

原 OJ 普通题仍沿用原来的输出归一化比较规则。三种模式均通过 lrun 执行，禁用网络并限制时间、内存与输出；沙箱不可用时返回系统错误，不回退到宿主机执行。

### 开发与提交语言

- 后端、任务编排、分析：Python 3.11+、FastAPI、SQLite。
- 前端：HTML、CSS、原生 JavaScript，内置 Markdown / KaTeX 资源。
- 评测底层：C/C++ 的 lrun、lrun-mirrorfs、ljudge、linteractive、lworkflow 与 testlib。交互、run-twice、多阶段通信的进程和管道生命周期由原生 `lworkflow` 管理。
- 当前 newjudge 提交语言：**C17、C++17、Python 3、PyPy 3、Java 21**，均支持普通、交互、run-twice 通信题。上传的 gen/val/checker/interactor 使用 C++17。
- 保留 `run-docker.ps1` 的普通题 Docker 后端及原 C、C++、PyPy、Java 支持；`run-local.ps1` 仅供可信代码开发测试。testlib、交互和通信题需要 newjudge 模式。

PyPy 使用 `/usr/bin/pypy3`，语法检查也在 PyPy 沙箱中执行；`.py` 文件在工作台可选择 Python 3 或 PyPy 3。参考标程上传后可在「查看 / 编辑」中选择解释器，导出题包的 `program_languages` 会保留语言选择。

Java 使用 OpenJDK 21，源码入口为无 `package` 声明的 `Main` 类。`javac` 在沙箱中编译，内部类和辅助类一起缓存；每次运行使用独立的 classes 目录。题目内存限制覆盖整个 JVM（含堆、线程、JIT 等），CPU 限制包括 JVM 启动开销；当前没有语言倍率。设置 `-Xmx` 上限、串行 GC 和单 CPU 参数以适配沙箱。交互程序仍需及时 `System.out.flush()`。

提交 API 使用 `"language": "pypy"` 或 `"language": "java"`。工作台试运行的 `solution` / `receiver` 使用 `{name, language, content}`，Java 文件名建议 `Main.java`，PyPy 为 `main.py`。参考标程也支持这两种语言；testlib 组件继续使用 C++。

原生 `ljudge` / `linteractive` 根据扩展名选择配置：`.py` / `.py3` 对应 CPython，`.pypy` / `.pypy3` 对应 PyPy，`.java` 对应 Java 21。Java 默认按 `--max-memory` 设置堆上限，也支持 `--max-jvm-memory` 显式指定字节数；cgroup 总内存限制始终生效。

## 集训队关联

保留队员档案、平台 Rating、拟合趋势、比赛复盘、导入导出和平台同步。

在队员档案的 **OJ 用户名**中填写 Sakura 登录用户名，新提交的最终结果自动进入队员档案和提交分析。已有提交可点击“OJ 导入/同步”补齐。多个档案绑定同一用户名时，系统不猜测归属。迁移前没有用户信息的旧提交保留手工归属，没有归属的显示为“未归属”。

Codeforces、AtCoder 使用 handle 同步。牛客使用独立的 **牛客 UID** 字段：填写个人竞赛主页 `https://ac.nowcoder.com/acm/contest/profile/<UID>` 中的数字 ID；昵称仅用于显示，同步成功后自动更新。成员列表支持按 UID 搜索，JSON / CSV 导出包含 UID。

牛客默认直接请求竞赛主页使用的 `rating-basic?uid=...` 和 `rating-history?uid=...` 接口，无需配置代理地址。同步当前 Rating、历史峰值、最近涨跌及完整的 Rating 比赛历史；个人 UID 只计算个人 Rating，不混入团队账号的分数。官方未提供的参赛人数记录为未知。队员画像可单独点击“同步牛客 Rating”，完成后自动刷新；全队同步仅查询已绑定的平台。

升级时，旧 `nowcoder_handle` 中的纯数字 ID 会一次性迁入 `nowcoder_uid`，普通昵称保持不变，需要另行填写 UID。换绑或清空 UID 会清除该成员原有的牛客分数与比赛记录；接口出错或历史不完整时保留上次完整同步结果。

仍可用 `SAKURA_NOWCODER_API_URL` 指定自定义服务，该服务现在接收 `uid` 查询参数，返回 `rating` 和可选 `peak_rating` / `rating_change` / `contest_count` / `nickname` / `history`。历史项使用 `contest_id`、`name`、`time`（毫秒时间戳或含时区的 ISO 时间）、`rank`、`old_rating`、`new_rating`；不再生成虚构的比赛 ID、时间或参赛人数。

## 目录与部署配置

```text
app/                 OJ API、前端、账号和评测调度
app/studio/          testlib 录题工作台、组卷与 Invocations
app/team/            集训队 API、分析与平台数据获取
judge/newjudge/      评测机源码、testlib 和原生命令行示例
scripts/             安装、原生验收和发布检查工具
tests/               合成数据的单元、API 与评测回归测试
data/                数据库、录题材料和任务结果（运行时生成，不入库）
runtime/             本地临时运行目录（运行时生成，不入库）
```

Linux 安装目录：

```text
/opt/sakura/venv             Python 环境
/opt/sakura/runtime          评测程序和生成的语言配置
/var/lib/sakura/judge        编译缓存、临时运行文件
/etc/sakura.env              私有部署配置
/etc/systemd/system/sakura.service
```

编译和运行指令从 `/opt/sakura/runtime/etc/ljudge` 读取，每行一个参数，不经过 shell。安装脚本为当前支持的五种语言生成配置，不依赖上游遗留服务器目录。上游 MySQL/Oracle 的专用连接配置未收入公开版本。

更新源码后可重新运行安装脚本构建评测机；`--skip-build` 复用已安装的二进制，`--port` 指定端口。与上游的集成差异见 [judge/SYNC.md](judge/SYNC.md)。

备份时停止服务并备份整个 `data/`；在线备份 SQLite 应使用 backup API，不能忽略 WAL 只复制数据库。备份、日志、截图、题包和测试报告应始终留在 Git 之外。

## API

原 `/api/auth/*`、`/api/users`、`/api/problems`、`/api/submissions` 保留。公开题面不返回隐藏数据和评测程序。

- `/api/studio/bootstrap`：引擎状态、模板、CSRF token。
- `/api/studio/problems`：创建/列出草稿；`/{id}` 读取或保存。
- `/api/studio/problems/{id}/generate`、`/submit`、`/jobs`：生成、临时代码试运行、任务记录。
- `POST /api/studio/problems/{id}/invoke`：批量评测，传入 `revision` 和 `solution_ids`（解法 ID 数组或 `"all"`）。
- `/api/studio/papers`：GET 列表、POST 新建；`/{id}` GET 读取、PUT 保存（包含 `revision`）。试卷字段为 `title`、`description`、有序 `problem_ids` 数组；也可传 `problem_codes` 按公开题目编号组卷。
- `/api/studio/papers/{id}/preview`、`/export`：预览和导出整卷；POST `/delete` 携带 `revision` 删除试卷。
- `/api/studio/problems/{id}/publish`：发布当前已验证数据；`/export` 导出题包。
- `/api/team/members`、`/overview`、`/ratings/*`、`/contests`、`/submissions`：集训队功能统一加 `/api/team` 前缀。
- `/api/team/integrations/oj/sync`：补齐本地 OJ 提交及归属。

Studio 写请求使用登录 cookie、`X-CSRF-Token` 和 JSON，请携带当前 `revision`；跨站写请求被拒绝。普通、交互、通信均通过同一个 OJ 提交接口，例如：

```json
{
  "problem_slug": "sum-two",
  "language": "python",
  "source_code": "a,b=map(int,input().split()); print(a+b)"
}
```

## 验证

普通单元与 API 回归使用临时数据库：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest
```

Windows 使用 `.venv\Scripts\python.exe` 执行同样命令。需要 gcc、g++、PyPy、Java 的测试在缺少工具链时跳过。

在已经配置好 newjudge 的 Linux/WSL 环境中运行真实沙箱回归：

```bash
sudo -u sakura env SAKURA_REAL_JUDGE=1 /opt/sakura/venv/bin/python -m pytest tests/test_newjudge_flow.py tests/test_newjudge_multipass.py tests/test_newjudge_communication.py tests/test_newjudge_solutions.py
sudo -u sakura /opt/sakura/venv/bin/python scripts/verify_native.py
```

覆盖普通、交互和通信流程、多语言、资源超限、主标程、自定义解法、发布隔离和文件/网络隔离。不要在多人共享实例繁忙时运行耗时的真实沙箱测试。

提交源码前先暂存改动，再检查 Git 暂存区中的实际内容：

```bash
git add .
python3 scripts/check_public_tree.py
```

当前任务队列位于单个应用进程中；远程评测节点、持久化分布式队列和公开比赛权限需要另行扩展。第三方组件的许可证和版权声明保留在各自目录中。
