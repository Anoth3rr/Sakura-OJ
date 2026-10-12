"""Read ljudge's administrator-owned language profiles (one argv token per line)."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re


class LanguageError(ValueError):
    pass


def language_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_+.-]{0,79}', value):
        raise LanguageError('语言标识必须是 ljudge 配置目录名')
    if '..' in value:
        raise LanguageError('语言标识不能包含 ..')
    return value


def infer_language(name):
    name = Path(name.replace('\\', '/')).name
    if name.startswith('mainv8.js'):
        return 'v8js'
    suffix = name.partition('.')[2]
    return {'py': 'python', 'cc': 'cpp', 'cxx': 'cpp'}.get(suffix, suffix)


def expand(tokens, mappings):
    # This is argv substitution, never shell evaluation.
    return [re.sub(r'\$(?:src|exe|dir|chroot|jvmmemory)\b',
                   lambda m: str(mappings[m[0][1:]]), token) for token in tokens]


@dataclass
class Profile:
    id: str
    paths: dict
    contents: dict
    src: str
    exe: str
    fingerprint: str

    def lines(self, key):
        return [line.lstrip(' ') for line in self.contents.get(key, '').splitlines()
                if line.strip() and not line.startswith('#')]

    def value(self, key, fallback=''):
        return self.contents.get(key, '').strip() or fallback

    def command(self, stage):
        if stage == 'run':
            return self.lines('run.stream.cmd_list') or self.lines('run.cmd_list') or ['./$exe']
        return self.lines('compile.cmd_list')

    def lrun_args(self, stage, mappings):
        result = []
        # Native ljudge omits fanotify filters when a readable boot config says
        # the running kernel lacks permission events. Keep the same behavior.
        import os
        boot_config = Path('/boot/config-' + os.uname().release)
        try:
            fanotify = 'CONFIG_FANOTIFY_ACCESS_PERMISSIONS=y' in boot_config.read_text()
        except OSError:
            fanotify = True
        for key in (stage + '.lrun_args', 'extra.lrun_args'):
            tokens = expand(self.lines(key), mappings)
            index = 0
            while index < len(tokens):
                option = tokens[index]
                count = 2 if option == '--fopen-filter' else 1 if option in (
                    '--syscalls', '--domainname', '--hostname', '--ostype', '--osrelease', '--osversion', '--max-stack') else 0
                # Same allowlist and stop-at-unknown semantics as native ljudge.
                if not count or index + count >= len(tokens):
                    break
                if option != '--fopen-filter' or fanotify:
                    result += tokens[index:index + count + 1]
                index += count + 1
        return result


class Languages:
    FILES = ('version.cmd_list', 'version.name', 'compile.src_name', 'compile.exe_name',
             'compile.cmd_list', 'run.cmd_list', 'run.stream.cmd_list',
             'compile.mirrorfs', 'run.mirrorfs', 'compile.lrun_args', 'run.lrun_args',
             'extra.lrun_args', 'compilefake_passwd', 'runfake_passwd',
             'compile.fs_override', 'run.fs_override')

    def __init__(self, directory):
        self.directory = Path(directory).resolve()

    def resolve(self, language):
        language_id(language)
        # Preserve the optional Python 3 alias; .py in native ljudge
        # remains available by explicitly selecting the native profile "py".
        native = 'py3' if language == 'python' else language
        parts = native.split('.')
        suffixes = ['.'.join(parts[i:]) for i in range(len(parts))]
        folders = [self.directory / suffix for suffix in suffixes]
        if not any((folder / 'version.cmd_list').is_file() for folder in folders):
            raise LanguageError(f'未配置语言 {language}：{self.directory}')
        paths, contents = {}, {}
        digest = hashlib.sha256(str(self.directory).encode())
        for key in self.FILES:
            path = next((folder / key for folder in [*folders, self.directory / '_default']
                         if (folder / key).exists()), None)
            if path is None:
                continue
            paths[key] = path
            if path.is_dir():
                for entry in sorted(path.iterdir()):
                    digest.update(entry.name.encode() + b'\0' + entry.read_bytes())
            else:
                contents[key] = path.read_text()
                digest.update(key.encode() + b'\0' + contents[key].encode())
        src = contents.get('compile.src_name', '').strip() or 'a.' + native.rsplit('.', 1)[-1]
        exe = contents.get('compile.exe_name', '').strip() or 'a.out'
        for filename in (src, exe):
            if filename in ('.', '..') or Path(filename).name != filename or '\\' in filename or '\0' in filename:
                raise LanguageError('compile.src_name / compile.exe_name 必须是文件名')
        return Profile(language, paths, contents, src, exe, digest.hexdigest())

    def catalog(self):
        result = []
        if not self.directory.is_dir():
            return result
        for folder in sorted(self.directory.iterdir()):
            if folder.name.startswith('_') or not folder.is_dir():
                continue
            try:
                profile = self.resolve(folder.name)
            except LanguageError:
                continue
            command = profile.lines('version.cmd_list')
            label = profile.value('version.name', command[0] if command else folder.name)
            result.append(dict(id=folder.name, label=f'{label} ({folder.name})', name='main.' + folder.name))
        if any(item['id'] == 'py3' for item in result):
            result.append(dict(id='python', label='Python 3 (alias)', name='main.py'))
        return result
