"""Toolchains installed inside the newjudge filesystem (never host fallbacks)."""
import os
import platform
from pathlib import Path

MIB = 1024 * 1024
JAVA_ARCH = {'x86_64': 'amd64', 'AMD64': 'amd64', 'aarch64': 'arm64'}.get(platform.machine(), platform.machine())
JAVA_HOME = Path('/usr/lib/jvm') / f'java-21-openjdk-{JAVA_ARCH}'
JAVA = str(JAVA_HOME / 'bin/java')
JAVAC = str(JAVA_HOME / 'bin/javac')
LANGUAGES = {
    'c': ('C17', 'main.c', ('/usr/bin/gcc',)),
    'cpp': ('C++17', 'main.cpp', ('/usr/bin/g++',)),
    'python': ('Python 3', 'main.py', ('/usr/bin/python3',)),
    'pypy': ('PyPy 3', 'main.py', ('/usr/bin/pypy3',)),
    'java': ('Java 21', 'Main.java', (JAVA, JAVAC)),
}


def language_catalog():
    return [dict(id=key, label=label, available=os.name == 'posix' and
                 all(os.access(path, os.X_OK) for path in commands) and
                 (key != 'java' or Path('/etc/java-21-openjdk').is_dir()))
            for key, (label, _, commands) in LANGUAGES.items()]


def java_options(memory):
    # The cgroup limit still covers the entire JVM, including native/JIT memory.
    # Bound JVM ergonomics explicitly: the sandbox does not expose host /proc.
    return [f'-Xmx{max(1, memory // MIB)}m', '-Xms8m', '-Xss1m',
            '-XX:+UseSerialGC', '-XX:ActiveProcessorCount=1', '-XX:-UsePerfData',
            '-XX:ReservedCodeCacheSize=32m', '-XX:+ExitOnOutOfMemoryError',
            '-Dfile.encoding=UTF-8', '-Duser.home=/tmp', '-Djava.io.tmpdir=/tmp']
