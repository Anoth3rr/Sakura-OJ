"""Validate a source file without a database or application dependency."""

from pathlib import Path
from .languages import infer_language, language_id, LanguageError

MAX_SOURCE = 512 * 1024

class ProblemError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status

def source(value, role='solution'):
    if not isinstance(value, dict):
        raise ProblemError('程序文件格式不正确')
    name = str(value.get('name', 'main.cpp'))
    code = value.get('content', '')
    if not isinstance(code, str) or not code.strip() or len(code.encode()) > MAX_SOURCE or '\0' in code:
        raise ProblemError('源码不能为空，且不能超过 512 KiB')
    try:
        language = language_id(value.get('language', infer_language(name)))
    except LanguageError as exc:
        raise ProblemError(str(exc)) from exc
    return dict(name=Path(name.replace('\\', '/')).name[:100], content=code, language=language)
