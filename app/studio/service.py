"""One authoring service and one serialized sandbox shared by OJ and Studio."""
import logging
import os
import platform
import secrets
import threading

from .engine import Engine, JudgeError
from .jobs import Jobs
from .models import Store
from .papers import Papers


class Sandbox:
    def __init__(self, settings):
        self.lock = threading.RLock()
        self.engine = None
        self.error = ''
        try:
            if os.name != 'posix':
                raise JudgeError('真实评测需要 Linux / WSL；请通过 run.ps1 启动统一服务')
            self.engine = Engine(settings.newjudge_work, settings.newjudge_runtime,
                                 settings.newjudge_runtime / 'testlib.h')
            self.engine.prepare()
        except (OSError, JudgeError) as exc:
            self.error = str(exc)
            logging.warning('newjudge is unavailable: %s', exc)

    def health(self):
        result = (self.engine.health() if self.engine else
                  dict(ready=False, backend='newjudge / lrun', kernel=platform.release(),
                       languages=[]))
        return dict(result, ready=bool(result['ready'] and not self.error), error=self.error)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)

        def invoke(*args, **kwargs):
            with self.lock:
                if not self.health()['ready']:
                    raise JudgeError(self.error or '评测机未就绪')
                return getattr(self.engine, name)(*args, **kwargs)
        return invoke


class StudioService:
    def __init__(self, settings):
        self.store = Store(settings.studio_directory)
        self.papers = Papers(self.store)
        self.engine = Sandbox(settings)
        self.jobs = Jobs(self.store, self.engine)
        self.csrf = secrets.token_urlsafe(32)

    def shutdown(self):
        self.jobs.shutdown()
