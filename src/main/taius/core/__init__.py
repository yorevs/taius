# _*_ coding: utf-8 _*_
#
# $app_name v0.0.1
#
# Package: main.taius.core
"""Package initialization."""

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .paths import APP_NAME
    from .paths import CORE_DIR
    from .paths import CORE_LOG_PATH
    from .router_runtime import DEFAULT_ROUTING_THRESHOLD
    from .paths import MODEL_DIR
    from .validation import REQUIRED_SKILL_FUNCTIONS
    from .paths import RESOURCE_DIR
    from .paths import ROUTER_MODEL_PATH
    from .paths import ROUTER_TRAIN_PATH
    from .paths import SKILLS_HASH_PATH
    from .paths import SKILLS_MODEL_DIR
    from .paths import SKILLS_SOURCE_DIR
    from .paths import SNAPSHOT_BACKUP_DIR
    from .validation import SUPPORTED_SKILL_CONTRACT_VERSION
    from .training_monitor import TrainingLogMonitor


_EXPORTS = {
    'APP_NAME': ('paths', 'APP_NAME'),
    'CORE_DIR': ('paths', 'CORE_DIR'),
    'CORE_LOG_PATH': ('paths', 'CORE_LOG_PATH'),
    'DEFAULT_ROUTING_THRESHOLD': ('router_runtime', 'DEFAULT_ROUTING_THRESHOLD'),
    'MODEL_DIR': ('paths', 'MODEL_DIR'),
    'REQUIRED_SKILL_FUNCTIONS': ('validation', 'REQUIRED_SKILL_FUNCTIONS'),
    'RESOURCE_DIR': ('paths', 'RESOURCE_DIR'),
    'ROUTER_MODEL_PATH': ('paths', 'ROUTER_MODEL_PATH'),
    'ROUTER_TRAIN_PATH': ('paths', 'ROUTER_TRAIN_PATH'),
    'SKILLS_HASH_PATH': ('paths', 'SKILLS_HASH_PATH'),
    'SKILLS_MODEL_DIR': ('paths', 'SKILLS_MODEL_DIR'),
    'SKILLS_SOURCE_DIR': ('paths', 'SKILLS_SOURCE_DIR'),
    'SNAPSHOT_BACKUP_DIR': ('paths', 'SNAPSHOT_BACKUP_DIR'),
    'SUPPORTED_SKILL_CONTRACT_VERSION': ('validation', 'SUPPORTED_SKILL_CONTRACT_VERSION'),
    'TrainingLogMonitor': ('training_monitor', 'TrainingLogMonitor')
}

def __getattr__(name):
    """Dynamically resolve package exports."""
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
    'MODEL_DIR',
    'REQUIRED_SKILL_FUNCTIONS',
    'RESOURCE_DIR',
    'ROUTER_MODEL_PATH',
    'ROUTER_TRAIN_PATH',
    'SKILLS_HASH_PATH',
    'SKILLS_MODEL_DIR',
    'SKILLS_SOURCE_DIR',
    'SNAPSHOT_BACKUP_DIR',
    'SUPPORTED_SKILL_CONTRACT_VERSION',
    'TrainingLogMonitor',
    'commands',
    'log_views',
    'paths',
    'router',
    'router_runtime',
    'router_stats',
    'runtime',
    'skill_management',
    'skill_views',
    'skills',
    'snapshots',
    'status',
    'text',
    'training_monitor',
    'validation'
]
__version__ = '0.0.1'
