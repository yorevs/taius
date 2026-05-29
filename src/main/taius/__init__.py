# _*_ coding: utf-8 _*_
#
# $app_name v0.0.1
#
# Package: main.taius
"""Package initialization."""

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core.paths import APP_NAME
    from .core.paths import CORE_DIR
    from .core.paths import CORE_LOG_PATH
    from .taius_core import DEFAULT_ROUTING_THRESHOLD
    from .core.router_runtime import DEFAULT_ROUTING_THRESHOLD
    from .core.paths import MODEL_DIR
    from .core.validation import REQUIRED_SKILL_FUNCTIONS
    from .core.paths import RESOURCE_DIR
    from .taius_core import ROUTER_CONFIG_PATH
    from .core.paths import ROUTER_MODEL_PATH
    from .core.paths import ROUTER_TRAIN_PATH
    from .core.paths import SKILLS_HASH_PATH
    from .core.paths import SKILLS_MODEL_DIR
    from .core.paths import SKILLS_SOURCE_DIR
    from .core.paths import SNAPSHOT_BACKUP_DIR
    from .core.validation import SUPPORTED_SKILL_CONTRACT_VERSION
    from .core.training_monitor import TrainingLogMonitor


_EXPORTS = {
    'APP_NAME': ('core.paths', 'APP_NAME'),
    'CORE_DIR': ('core.paths', 'CORE_DIR'),
    'CORE_LOG_PATH': ('core.paths', 'CORE_LOG_PATH'),
    'DEFAULT_ROUTING_THRESHOLD': ('taius', 'DEFAULT_ROUTING_THRESHOLD'),
    'DEFAULT_ROUTING_THRESHOLD': ('core.router_runtime', 'DEFAULT_ROUTING_THRESHOLD'),
    'MODEL_DIR': ('core.paths', 'MODEL_DIR'),
    'REQUIRED_SKILL_FUNCTIONS': ('core.validation', 'REQUIRED_SKILL_FUNCTIONS'),
    'RESOURCE_DIR': ('core.paths', 'RESOURCE_DIR'),
    'ROUTER_CONFIG_PATH': ('taius', 'ROUTER_CONFIG_PATH'),
    'ROUTER_MODEL_PATH': ('core.paths', 'ROUTER_MODEL_PATH'),
    'ROUTER_TRAIN_PATH': ('core.paths', 'ROUTER_TRAIN_PATH'),
    'SKILLS_HASH_PATH': ('core.paths', 'SKILLS_HASH_PATH'),
    'SKILLS_MODEL_DIR': ('core.paths', 'SKILLS_MODEL_DIR'),
    'SKILLS_SOURCE_DIR': ('core.paths', 'SKILLS_SOURCE_DIR'),
    'SNAPSHOT_BACKUP_DIR': ('core.paths', 'SNAPSHOT_BACKUP_DIR'),
    'SUPPORTED_SKILL_CONTRACT_VERSION': ('core.validation', 'SUPPORTED_SKILL_CONTRACT_VERSION'),
    'TrainingLogMonitor': ('core.training_monitor', 'TrainingLogMonitor')
}

def __getattr__(name):
    if name in _EXPORTS:
        module, attr = _EXPORTS[name]
        mod = importlib.import_module(f"{__name__}.{module}")
        value = getattr(mod, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'APP_NAME',
    'CORE_DIR',
    'CORE_LOG_PATH',
    'DEFAULT_ROUTING_THRESHOLD',
    'DEFAULT_ROUTING_THRESHOLD',
    'MODEL_DIR',
    'REQUIRED_SKILL_FUNCTIONS',
    'RESOURCE_DIR',
    'ROUTER_CONFIG_PATH',
    'ROUTER_MODEL_PATH',
    'ROUTER_TRAIN_PATH',
    'SKILLS_HASH_PATH',
    'SKILLS_MODEL_DIR',
    'SKILLS_SOURCE_DIR',
    'SNAPSHOT_BACKUP_DIR',
    'SUPPORTED_SKILL_CONTRACT_VERSION',
    'TrainingLogMonitor',
    'core',
    'skills',
    'taius_core.py'
]
__version__ = '0.0.1'
