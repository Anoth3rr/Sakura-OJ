from pathlib import Path
import os


def is_path_exist(path: str) -> bool:
    return Path(path).is_dir()


def mk_dir(path: str) -> bool:
    if is_path_exist(path):
        return False
    Path(path).mkdir()
    return True


def rm_dir(path: str) -> bool:
    # os.RemoveAll("/foo/123_*")
    os.rmdir(path)
    return True


if __name__ == '__main__':
    rm_dir("123")
    print(mk_dir("123"))
