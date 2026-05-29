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
    from .taius_core import console
    from .taius_core import forget_router
    from .taius_core import get_routing_threshold
    from .taius_core import load_router_config
    from .taius_core import load_router_model
    from .taius_core import predict_skill_with_router
    from .taius_core import route_to_skill
    from .taius_core import router_needs_training
    from .taius_core import save_router_config
    from .taius_core import teach_router
    from .taius_core import train_router
    from .taius_core import train_router_from_existing_file
    from .taius_core import train_router_if_needed


_EXPORTS = {
    "APP_NAME": ("core.paths", "APP_NAME"),
    "CORE_DIR": ("core.paths", "CORE_DIR"),
    "CORE_LOG_PATH": ("core.paths", "CORE_LOG_PATH"),
    "DEFAULT_ROUTING_THRESHOLD": ("core.router_runtime", "DEFAULT_ROUTING_THRESHOLD"),
    "MODEL_DIR": ("core.paths", "MODEL_DIR"),
    "REQUIRED_SKILL_FUNCTIONS": ("core.validation", "REQUIRED_SKILL_FUNCTIONS"),
    "RESOURCE_DIR": ("core.paths", "RESOURCE_DIR"),
    "ROUTER_CONFIG_PATH": ("taius_core", "ROUTER_CONFIG_PATH"),
    "ROUTER_MODEL_PATH": ("core.paths", "ROUTER_MODEL_PATH"),
    "ROUTER_TRAIN_PATH": ("core.paths", "ROUTER_TRAIN_PATH"),
    "SKILLS_HASH_PATH": ("core.paths", "SKILLS_HASH_PATH"),
    "SKILLS_MODEL_DIR": ("core.paths", "SKILLS_MODEL_DIR"),
    "SKILLS_SOURCE_DIR": ("core.paths", "SKILLS_SOURCE_DIR"),
    "SNAPSHOT_BACKUP_DIR": ("core.paths", "SNAPSHOT_BACKUP_DIR"),
    "SUPPORTED_SKILL_CONTRACT_VERSION": ("core.validation", "SUPPORTED_SKILL_CONTRACT_VERSION"),
    "TrainingLogMonitor": ("core.training_monitor", "TrainingLogMonitor"),
    "console": ("taius_core", "console"),
    "forget_router": ("taius_core", "forget_router"),
    "get_routing_threshold": ("taius_core", "get_routing_threshold"),
    "load_router_config": ("taius_core", "load_router_config"),
    "load_router_model": ("taius_core", "load_router_model"),
    "predict_skill_with_router": ("taius_core", "predict_skill_with_router"),
    "route_to_skill": ("taius_core", "route_to_skill"),
    "router_needs_training": ("taius_core", "router_needs_training"),
    "save_router_config": ("taius_core", "save_router_config"),
    "teach_router": ("taius_core", "teach_router"),
    "train_router": ("taius_core", "train_router"),
    "train_router_from_existing_file": ("taius_core", "train_router_from_existing_file"),
    "train_router_if_needed": ("taius_core", "train_router_if_needed"),
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
    "APP_NAME",
    "CORE_DIR",
    "CORE_LOG_PATH",
    "DEFAULT_ROUTING_THRESHOLD",
    "MODEL_DIR",
    "REQUIRED_SKILL_FUNCTIONS",
    "RESOURCE_DIR",
    "ROUTER_CONFIG_PATH",
    "ROUTER_MODEL_PATH",
    "ROUTER_TRAIN_PATH",
    "SKILLS_HASH_PATH",
    "SKILLS_MODEL_DIR",
    "SKILLS_SOURCE_DIR",
    "SNAPSHOT_BACKUP_DIR",
    "SUPPORTED_SKILL_CONTRACT_VERSION",
    "TrainingLogMonitor",
    "console",
    "forget_router",
    "get_routing_threshold",
    "load_router_config",
    "load_router_model",
    "predict_skill_with_router",
    "route_to_skill",
    "router_needs_training",
    "save_router_config",
    "teach_router",
    "train_router",
    "train_router_from_existing_file",
    "train_router_if_needed",
]

__version__ = "0.0.1"
