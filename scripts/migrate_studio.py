"""Take a consistent, non-destructive copy of a stopped/idle legacy Studio."""
import argparse
from pathlib import Path
import shutil
import sqlite3


def migrate(source, target):
    if (target / 'studio.sqlite3').exists():
        raise SystemExit('目标已有题库，拒绝覆盖：' + str(target))
    with sqlite3.connect((source / 'studio.sqlite3').as_uri() + '?mode=ro', uri=True) as src:
        if src.execute("SELECT count(*) FROM jobs WHERE state IN ('queued','running')").fetchone()[0]:
            raise SystemExit('录题工作台还有未完成任务，请等待任务结束')
        target.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(target / 'studio.sqlite3') as dest:
            src.backup(dest)
        shutil.copytree(source / 'datasets', target / 'datasets')
        print({t: src.execute('SELECT count(*) FROM ' + t).fetchone()[0] for t in ('problems', 'jobs')})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--target', type=Path, required=True)
    args = parser.parse_args()
    migrate(args.source.resolve(), args.target.resolve())
