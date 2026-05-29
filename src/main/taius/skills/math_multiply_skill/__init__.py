# _*_ coding: utf-8 _*_
#
# $app_name v0.0.1
#
# Package: main.taius.skills.math_multiply_skill
"""Package initialization."""

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .skill import CONFIG
    from .skill import CONTRACT_VERSION
    from .skill import EXAMPLES
    from .skill import MODEL
    from .skill import SKILL_ID
    from .skill import SKILL_VERSION
    from .skill import SYMBOL
    from .skill import VERBS


_EXPORTS = {
    'CONFIG': ('skill', 'CONFIG'),
    'CONTRACT_VERSION': ('skill', 'CONTRACT_VERSION'),
    'EXAMPLES': ('skill', 'EXAMPLES'),
    'MODEL': ('skill', 'MODEL'),
    'SKILL_ID': ('skill', 'SKILL_ID'),
    'SKILL_VERSION': ('skill', 'SKILL_VERSION'),
    'SYMBOL': ('skill', 'SYMBOL'),
    'VERBS': ('skill', 'VERBS')
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
    'CONFIG',
    'CONTRACT_VERSION',
    'EXAMPLES',
    'MODEL',
    'SKILL_ID',
    'SKILL_VERSION',
    'SYMBOL',
    'VERBS',
    'skill'
]
__version__ = '0.0.1'
