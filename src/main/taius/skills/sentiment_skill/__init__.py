# _*_ coding: utf-8 _*_
#
# $app_name v0.0.1
#
# Package: main.taius.skills.sentiment_skill
"""Package initialization."""

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .skill import CONFIG
    from .skill import MODEL_PATH
    from .skill import SKILL_ID
    from .skill import SKILL_VERSION
    from .skill import TRAIN_PATH
    from .skill import VERSION_PATH


_EXPORTS = {
    'CONFIG': ('skill', 'CONFIG'),
    'MODEL_PATH': ('skill', 'MODEL_PATH'),
    'SKILL_ID': ('skill', 'SKILL_ID'),
    'SKILL_VERSION': ('skill', 'SKILL_VERSION'),
    'TRAIN_PATH': ('skill', 'TRAIN_PATH'),
    'VERSION_PATH': ('skill', 'VERSION_PATH')
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
    'CONFIG',
    'MODEL_PATH',
    'SKILL_ID',
    'SKILL_VERSION',
    'TRAIN_PATH',
    'VERSION_PATH',
    'skill'
]
__version__ = '0.0.1'
