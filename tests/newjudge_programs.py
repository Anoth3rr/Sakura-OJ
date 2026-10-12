"""Contestant fixtures for the real sandbox and native CLI smoke tests."""
PYPY_SUM = '''import sys
assert sys.implementation.name == "pypy"
n = int(input())
a = list(map(int, input().split()))
assert len(a) == n
print(sum(a), flush=True)
'''

JAVA_SUM = '''import java.io.*;
public class Main {
    static class Input {
        long next() throws IOException {
            int c;
            do { c = System.in.read(); } while (c >= 0 && c <= 32);
            if (c < 0) throw new EOFException();
            long x = 0;
            while (c > 32) { x = x * 10 + c - '0'; c = System.in.read(); }
            return x;
        }
    }
    public static void main(String[] args) throws Exception {
        if (Runtime.version().feature() != 21) throw new AssertionError("Java version");
        Input in = new Input();
        int n = (int)in.next();
        long 答案 = 0;
        while (n-- > 0) 答案 = Sum.add(答案, in.next());
        System.out.println(答案);
        System.out.flush();
    }
}
class Sum { static long add(long a, long b) { return a + b; } }
'''

PYPY_TWICE = '''import sys, os
from pathlib import Path
assert sys.implementation.name == 'pypy'
assert sys.argv[1] == os.environ['JUDGE_PHASE']
assert not Path('/tmp/sender-state').exists()
assert not Path('/work/sender-state').exists()
if sys.argv[1] == 'send':
    Path('/tmp/sender-state').write_text('private')
    Path('/work/sender-state').write_text('private')
    n = int(input())
    print(sum(map(int, input().split())))
elif sys.argv[1] == 'receive':
    print(int(input()))
    assert not sys.stdin.read()
else:
    raise AssertionError('unknown phase')
'''

JAVA_TWICE = '''import java.nio.file.*;
import java.util.*;
public class Main {
    static int state = 0;
    public static void main(String[] args) throws Exception {
        if (args.length != 1 || !args[0].equals(System.getenv("JUDGE_PHASE")))
            throw new AssertionError("phase");
        Path tmp = Path.of("/tmp/sender-state"), work = Path.of("/work/sender-state");
        if (state != 0 || Files.exists(tmp) || Files.exists(work)) throw new AssertionError("leaked state");
        Scanner in = new Scanner(System.in);
        if (args[0].equals("send")) {
            state = 42;
            Files.writeString(tmp, "private"); Files.writeString(work, "private");
            int n = in.nextInt(); long sum = 0;
            while (n-- > 0) sum += in.nextLong();
            System.out.println(sum);
        } else if (args[0].equals("receive")) {
            System.out.println(in.nextLong());
            if (in.hasNext()) throw new AssertionError("unexpected private input");
        } else throw new AssertionError("unknown phase");
    }
}
'''


def candidate(language, mode):
    code = {('pypy', False): PYPY_SUM, ('pypy', True): PYPY_TWICE,
            ('java', False): JAVA_SUM, ('java', True): JAVA_TWICE}[language, mode == 'communication']
    return dict(language=language, name='Main.java' if language == 'java' else 'main.py', content=code)


def java_main(body):
    return 'public class Main { public static void main(String[] args) throws Exception {' + body + '} }'
