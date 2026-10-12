"""Team settings share Sakura's data directory and OJ database."""
import os
from pathlib import Path
from ..config import PROJECT_ROOT, settings as oj_settings


def optional_path(name):
    value = os.getenv(name)
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


class Settings:
    app_name = 'Sakura 训练队中枢'
    _database_path = optional_path('SAKURA_DATABASE_PATH')
    _oj_database_path = optional_path('SAKURA_OJ_DATABASE_PATH')
    oj_base_url = os.getenv('SAKURA_OJ_BASE_URL', '').strip().rstrip('/')
    nowcoder_api_url = os.getenv('SAKURA_NOWCODER_API_URL', '').strip().rstrip('/')
    request_timeout_seconds = float(os.getenv('SAKURA_REQUEST_TIMEOUT', '8'))
    seed_demo = os.getenv('SAKURA_SEED_DEMO', 'false').lower() not in ('0', 'false', 'no', 'off')

    @property
    def database_path(self):
        return self._database_path or oj_settings.database_path.parent / 'team.sqlite3'

    @database_path.setter
    def database_path(self, value):
        self._database_path = value

    @property
    def oj_database_path(self):
        return self._oj_database_path or oj_settings.database_path

    @oj_database_path.setter
    def oj_database_path(self, value):
        self._oj_database_path = value

    def ensure_directories(self):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
