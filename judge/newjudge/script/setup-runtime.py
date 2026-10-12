#!/usr/bin/env python3
"""Create a local runtime directory using an already installed lrun sandbox."""
import argparse
import os
from pathlib import Path
import shutil
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'lib'))
from newjudge.compiler import MIRROR


def executable(parser, value, name):
    found = str(value) if value is not None else shutil.which(name)
    if not found:
        parser.error(f'找不到 {name}；请先配置 lrun，或通过参数指定已安装二进制的绝对路径')
    path = Path(found).resolve()
    if not path.is_file() or not os.access(path, os.X_OK):
        parser.error(f'不是可执行文件：{path}')
    return path


def main():
    parser = argparse.ArgumentParser(description='为独立 newjudge 准备本地运行目录；复用已安装的 lrun。')
    parser.add_argument('--runtime', type=Path,
                        default=Path(os.environ.get('NEWJUDGE_RUNTIME', REPO / 'runtime')))
    parser.add_argument('--lrun', type=Path)
    parser.add_argument('--mirrorfs', type=Path)
    parser.add_argument('--testlib', type=Path, default=REPO / 'ljudge/etc/ljudge/_default/testlib.h')
    args = parser.parse_args()
    if os.path.lexists(args.runtime):
        parser.error('运行目录已存在；已配置时无需再次执行，或用 --runtime 指定新目录')
    lrun = executable(parser, args.lrun, 'lrun')
    mirrorfs = executable(parser, args.mirrorfs, 'lrun-mirrorfs')
    if not args.testlib.is_file():
        parser.error(f'testlib 头文件不存在：{args.testlib}')
    runtime = args.runtime.resolve()
    runtime.mkdir(parents=True)
    (runtime / 'bin').mkdir()
    (runtime / 'bin/lrun').symlink_to(lrun)
    (runtime / 'bin/lrun-mirrorfs').symlink_to(mirrorfs)
    (runtime / 'mirrorfs.conf').write_text(MIRROR, encoding='utf-8')
    shutil.copyfile(args.testlib, runtime / 'testlib.h')
    print(f'运行目录：{runtime}')
    print(f'lrun：{lrun}')
    print(f'lrun-mirrorfs：{mirrorfs}')


if __name__ == '__main__':
    main()
