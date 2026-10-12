"""Small working testlib examples, also used by integration tests."""
from .models import DOMJUDGE_COMMUNICATION, TESTLIB_COMMUNICATION, new_problem, source

GEN = r'''#include "testlib.h"
#include <iostream>
using namespace std;
int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    int n = argc > 1 ? atoi(argv[1]) : 10;
    int upper = argc > 2 ? atoi(argv[2]) : 100;
    ensuref(1 <= n && n <= 100000, "n out of range");
    ensuref(1 <= upper && upper <= 1000000000, "upper out of range");
    cout << n << '\n';
    for (int i = 0; i < n; ++i)
        cout << rnd.next(1, upper) << (i + 1 == n ? '\n' : ' ');
}
'''
VAL = r'''#include "testlib.h"
int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    int n = inf.readInt(1, 100000, "n");
    inf.readEoln();
    for (int i = 0; i < n; ++i) {
        inf.readInt(1, 1000000000, "a");
        if (i + 1 == n) inf.readEoln();
        else inf.readSpace();
    }
    inf.readEof();
}
'''
CHECKER = r'''#include "testlib.h"
int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    long long expected = ans.readLong();
    long long actual = ouf.readLong();
    if (actual != expected) quitf(_wa, "expected %lld, found %lld", expected, actual);
    if (!ouf.seekEof()) quitf(_pe, "extra output");
    quitf(_ok, "sum is correct");
}
'''
REFERENCE = r'''#include <bits/stdc++.h>
using namespace std;
int main() {
    int n; cin >> n;
    long long sum = 0, x;
    while (n--) { cin >> x; sum += x; }
    cout << sum << endl;
}
'''
INTERACTOR = r'''#include "testlib.h"
#include <iostream>
using namespace std;
int main(int argc, char* argv[]) {
    registerInteraction(argc, argv);
    int n = inf.readInt();
    cout << n << '\n';
    long long sum = 0;
    for (int i = 0; i < n; ++i) {
        int a = inf.readInt();
        sum += a;
        cout << a << (i + 1 == n ? '\n' : ' ');
    }
    cout.flush(); // Always flush before waiting for the contestant.
    long long reply = ouf.readLong();
    tout << reply << endl; // checker reads this transcript.
    if (reply != sum) quitf(_wa, "incorrect sum");
    quitf(_ok, "dialogue completed");
}
'''
TWICE = r'''#include <bits/stdc++.h>
using namespace std;
int main(int argc, char* argv[]) {
    if (argc != 2) return 1;
    if (string(argv[1]) == "send") {
        int n; cin >> n;
        long long sum = 0, x;
        while (n--) { cin >> x; sum += x; }
        cout << sum << '\n'; // Only these bytes reach Receiver.
    } else if (string(argv[1]) == "receive") {
        long long sum; cin >> sum;
        cout << sum << '\n';
    } else return 1;
}
'''
STATEMENT = '''# 数列求和

给定一个包含 $n$ 个正整数的数列，求所有元素的和。

## 输入格式

第一行一个整数 $n$。第二行包含 $n$ 个整数 $a_1, a_2, \\ldots, a_n$。

## 输出格式

输出一个整数，表示数列的和。

## 样例

输入：
```text
5
1 2 3 4 5
```

输出：
```text
15
```

## 数据范围

$1 \\le n \\le 10^5$，$1 \\le a_i \\le 10^9$。请使用 64 位整数。
'''


def example(mode):
    p = new_problem()
    p['mode'] = mode
    p['title'] = {'normal': '数列求和', 'interactive': '对话中的求和', 'communication': '一封短消息'}[mode]
    p['statement'] = STATEMENT.replace('# 数列求和', '# ' + p['title'])
    if mode == 'interactive':
        p['statement'] += '''
## 交互协议

交互器向你的程序发送 $n$ 和数列。你需要输出总和，并 **flush** 输出缓冲区，然后正常退出。
在本示例中，interactor 同时将你的答案写入交互记录，由 checker 再次检查。
'''
    if mode == 'communication':
        p['statement'] += '''
## 通信协议（run-twice）

同一程序会被运行两次，使用 C/C++ 的 `argv[1]`、Python/PyPy 的 `sys.argv[1]`、Java 的 `args[0]` 区分阶段，也可读取环境变量 `JUDGE_PHASE`：

1. `send`：标准输入是完整测试数据，将消息写入标准输出。
2. `receive`：在全新沙箱中启动，标准输入 **只有消息**，输出数列的和。

消息最多 32 字节（包括空格和换行）。两次运行不能共享文件或内存。
时间、内存限制分别作用于每个阶段。
'''
        p['message_bytes'] = 32
    programs = dict(gen=GEN, val=VAL, checker=CHECKER, reference=TWICE if mode == 'communication' else REFERENCE)
    if mode == 'interactive':
        programs['interactor'] = INTERACTOR
    p['programs'] = {role: source(dict(name=role + '.cpp', content=content), role) for role, content in programs.items()}
    return p


def candidate(mode):
    return dict(name='main.cpp', content=TWICE if mode == 'communication' else REFERENCE)


MULTIPASS_SOLUTION = r'''#include <iostream>
#include <string>
using namespace std;
int main() {
    string phase;
    if (!(cin >> phase)) return 1;
    long long sum = 0, x;
    if (phase == "send") {
        int n; cin >> n;
        while (n--) { cin >> x; sum += x; }
    } else if (phase == "receive") cin >> sum;
    else return 1;
    cout << sum << '\n';
}
'''

MULTIPASS_VALIDATOR = r'''#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
using namespace std;
int main(int argc, char** argv) {
    if (argc != 4) return 1;
    ifstream input(argv[1]);
    string feedback = argv[3], phase;
    input >> phase;
    string output((istreambuf_iterator<char>(cin)), {});
    istringstream stream(output);
    long long actual, expected = 0, x;
    string extra;
    if (!(stream >> actual) || (stream >> extra)) return 43;
    if (phase == "send") {
        int n; input >> n;
        while (n--) { input >> x; expected += x; }
        if (output.size() > 32 || actual != expected) return 43;
        ofstream state(feedback + "/expected"); state << expected << '\n';
        ofstream next(feedback + "/nextpass.in"); next << "receive\n" << output;
        if (!state || !next) return 1;
    } else if (phase == "receive") {
        ifstream state(feedback + "/expected");
        if (!(state >> expected)) return 1;
        if (actual != expected) return 43;
        ofstream(feedback + "/judgemessage.txt") << "Both passes accepted\n";
    } else return 1;
    return 42;
}
'''


def multipass_example():
    p = new_problem()
    p.update(mode='communication', title='经过验证的短消息',
             communication_protocol=DOMJUDGE_COMMUNICATION, validation_passes=2)
    p['statement'] = '''# 经过验证的短消息

同一程序在两个独立进程中运行。第一阶段输入首行为 `send`，随后是数列长度
和数列；输出不超过 32 字节的消息。输出 validator 验证消息后构造第二阶段输入。
第二阶段输入首行为 `receive`，随后只有传递的消息；输出数列的和。

每阶段都有独立的时间和内存限制，不能共享文件或内存。阶段由输入中的标记决定。
本示例传递十进制的总和；validator 检查每阶段的结果和第一阶段消息长度。
'''
    gen = GEN.replace("cout << n << '\\n';", 'cout << "send\\n" << n << \'\\n\';')
    val = VAL.replace('int n = inf.readInt', 'ensuref(inf.readToken() == "send", "expected phase"); inf.readEoln();\n    int n = inf.readInt')
    programs = dict(gen=gen, val=val, checker=MULTIPASS_VALIDATOR, reference=MULTIPASS_SOLUTION)
    p['programs'] = {role: source(dict(name=role + '.cpp', content=code), role) for role, code in programs.items()}
    return p


TESTLIB_COMMUNICATION_INTERACTOR = r'''#include "testlib.h"
#include <iostream>
using namespace std;
int main(int argc, char* argv[]) {
    registerInteraction(argc, argv);
    int n = inf.readInt();
    cout << "send\n" << n << '\n';
    for (int i = 0; i < n; ++i)
        cout << inf.readInt() << (i + 1 == n ? '\n' : ' ');
    cout.flush();
    // The interactor owns the message protocol and its size limit.
    string message = ouf.readToken("[0-9]{1,20}", "message");
    tout << "receive\n" << message << '\n';
    quitf(_ok, "message forwarded");
}
'''

TESTLIB_COMMUNICATION_SOLUTION = MULTIPASS_SOLUTION.replace("cout << sum << '\\n';", 'cout << sum << endl;')


def testlib_communication_example():
    p = example('normal')
    p.update(mode='communication', title='交互转交的短消息', communication_protocol=TESTLIB_COMMUNICATION)
    p['statement'] = '''# 交互转交的短消息

同一程序运行两次，每次使用独立的进程和工作目录。

首轮交互器发送 `send`、数列长度及数列。程序输出一个不超过 20 位的非负十进制整数，
表示要传递的消息，并刷新输出。交互器检查消息格式，将 `receive` 和消息写入 `tout`。

第二轮程序从标准输入读取 `receive` 和消息，输出原数列的总和。checker 检查第二轮答案。
阶段由输入中的标记决定；两轮不能共享文件或内存，每轮分别计算时间和内存限制。

输入数列满足 $1 \\le n \\le 10^5$、$1 \\le a_i \\le 10^9$。
参考标程按普通输入输出生成答案；完整两轮选手代码填入 Solution 的待测程序。
'''
    p['programs']['interactor'] = source(dict(name='interactor.cpp', content=TESTLIB_COMMUNICATION_INTERACTOR), 'interactor')
    return p
