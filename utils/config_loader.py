"""
Configuration loader with environment variable overrides and validation.
"""
import os
import json
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    host: str = 'localhost'
    port: int = 8080
    debug: bool = False
    db_url: str = ''
    max_connections: int = 10
    request_timeout: int = 30
    log_level: str = 'INFO'
    allowed_origins: list = field(default_factory=list)

    def validate(self) -> None:
        if not self.db_url:
            raise ValueError('db_url is required')
        if not (1 <= self.port <= 65535):
            raise ValueError(f'Invalid port: {self.port}')
        if self.max_connections < 1:
            raise ValueError('max_connections must be >= 1')


def load_config(path: Optional[str] = None) -> AppConfig:
    """Load config from JSON file, then override with environment variables."""
    data = {}
    if path and os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        logger.info('Loaded config from %s', path)

    overrides = {
        'host':            os.environ.get('APP_HOST'),
        'port':            int(os.environ['APP_PORT']) if 'APP_PORT' in os.environ else None,
        'debug':           os.environ.get('APP_DEBUG', '').lower() == 'true' or None,
        'db_url':          os.environ.get('DATABASE_URL'),
        'max_connections': int(os.environ['MAX_CONN']) if 'MAX_CONN' in os.environ else None,
        'log_level':       os.environ.get('LOG_LEVEL'),
    }
    data.update({k: v for k, v in overrides.items() if v is not None})

    cfg = AppConfig(**{k: v for k, v in data.items() if hasattr(AppConfig, k)})
    cfg.validate()
    return cfg
