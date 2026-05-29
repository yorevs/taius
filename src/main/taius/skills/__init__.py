# _*_ coding: utf-8 _*_
#
# $app_name v0.0.1
#
# Package: main.taius.skills
"""Package initialization."""

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._template.skill import CONFIG
    from .math_subtract_skill.skill import CONFIG
    from .math_sum_skill.skill import CONFIG
    from .sentiment_skill.skill import CONFIG
    from .math_multiply_skill.skill import CONFIG
    from .math_divide_skill.skill import CONFIG
    from .math_subtract_skill.skill import CONTRACT_VERSION
    from .math_sum_skill.skill import CONTRACT_VERSION
    from .math_multiply_skill.skill import CONTRACT_VERSION
    from .math_divide_skill.skill import CONTRACT_VERSION
    from .math_subtract_skill.skill import EXAMPLES
    from .math_sum_skill.skill import EXAMPLES
    from .math_multiply_skill.skill import EXAMPLES
    from .math_divide_skill.skill import EXAMPLES
    from .math_subtract_skill.skill import MODEL
    from .math_sum_skill.skill import MODEL
    from .math_multiply_skill.skill import MODEL
    from .math_divide_skill.skill import MODEL
    from .sentiment_skill.skill import MODEL_PATH
    from .math_subtract_skill.skill import SKILL_ID
    from .math_sum_skill.skill import SKILL_ID
    from .sentiment_skill.skill import SKILL_ID
    from .math_multiply_skill.skill import SKILL_ID
    from .math_divide_skill.skill import SKILL_ID
    from .echo_skill.skill import SKILL_ID
    from .math_subtract_skill.skill import SKILL_VERSION
    from .math_sum_skill.skill import SKILL_VERSION
    from .sentiment_skill.skill import SKILL_VERSION
    from .math_multiply_skill.skill import SKILL_VERSION
    from .math_divide_skill.skill import SKILL_VERSION
    from .echo_skill.skill import SKILL_VERSION
    from .math_subtract_skill.skill import SYMBOL
    from .math_sum_skill.skill import SYMBOL
    from .math_multiply_skill.skill import SYMBOL
    from .math_divide_skill.skill import SYMBOL
    from .sentiment_skill.skill import TRAIN_PATH
    from .math_subtract_skill.skill import VERBS
    from .math_sum_skill.skill import VERBS
    from .math_multiply_skill.skill import VERBS
    from .math_divide_skill.skill import VERBS
    from .sentiment_skill.skill import VERSION_PATH


_EXPORTS = {
    'CONFIG': ('_template.skill', 'CONFIG'),
    'CONFIG': ('math_subtract_skill.skill', 'CONFIG'),
    'CONFIG': ('math_sum_skill.skill', 'CONFIG'),
    'CONFIG': ('sentiment_skill.skill', 'CONFIG'),
    'CONFIG': ('math_multiply_skill.skill', 'CONFIG'),
    'CONFIG': ('math_divide_skill.skill', 'CONFIG'),
    'CONTRACT_VERSION': ('math_subtract_skill.skill', 'CONTRACT_VERSION'),
    'CONTRACT_VERSION': ('math_sum_skill.skill', 'CONTRACT_VERSION'),
    'CONTRACT_VERSION': ('math_multiply_skill.skill', 'CONTRACT_VERSION'),
    'CONTRACT_VERSION': ('math_divide_skill.skill', 'CONTRACT_VERSION'),
    'EXAMPLES': ('math_subtract_skill.skill', 'EXAMPLES'),
    'EXAMPLES': ('math_sum_skill.skill', 'EXAMPLES'),
    'EXAMPLES': ('math_multiply_skill.skill', 'EXAMPLES'),
    'EXAMPLES': ('math_divide_skill.skill', 'EXAMPLES'),
    'MODEL': ('math_subtract_skill.skill', 'MODEL'),
    'MODEL': ('math_sum_skill.skill', 'MODEL'),
    'MODEL': ('math_multiply_skill.skill', 'MODEL'),
    'MODEL': ('math_divide_skill.skill', 'MODEL'),
    'MODEL_PATH': ('sentiment_skill.skill', 'MODEL_PATH'),
    'SKILL_ID': ('math_subtract_skill.skill', 'SKILL_ID'),
    'SKILL_ID': ('math_sum_skill.skill', 'SKILL_ID'),
    'SKILL_ID': ('sentiment_skill.skill', 'SKILL_ID'),
    'SKILL_ID': ('math_multiply_skill.skill', 'SKILL_ID'),
    'SKILL_ID': ('math_divide_skill.skill', 'SKILL_ID'),
    'SKILL_ID': ('echo_skill.skill', 'SKILL_ID'),
    'SKILL_VERSION': ('math_subtract_skill.skill', 'SKILL_VERSION'),
    'SKILL_VERSION': ('math_sum_skill.skill', 'SKILL_VERSION'),
    'SKILL_VERSION': ('sentiment_skill.skill', 'SKILL_VERSION'),
    'SKILL_VERSION': ('math_multiply_skill.skill', 'SKILL_VERSION'),
    'SKILL_VERSION': ('math_divide_skill.skill', 'SKILL_VERSION'),
    'SKILL_VERSION': ('echo_skill.skill', 'SKILL_VERSION'),
    'SYMBOL': ('math_subtract_skill.skill', 'SYMBOL'),
    'SYMBOL': ('math_sum_skill.skill', 'SYMBOL'),
    'SYMBOL': ('math_multiply_skill.skill', 'SYMBOL'),
    'SYMBOL': ('math_divide_skill.skill', 'SYMBOL'),
    'TRAIN_PATH': ('sentiment_skill.skill', 'TRAIN_PATH'),
    'VERBS': ('math_subtract_skill.skill', 'VERBS'),
    'VERBS': ('math_sum_skill.skill', 'VERBS'),
    'VERBS': ('math_multiply_skill.skill', 'VERBS'),
    'VERBS': ('math_divide_skill.skill', 'VERBS'),
    'VERSION_PATH': ('sentiment_skill.skill', 'VERSION_PATH')
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
    'CONFIG',
    'CONFIG',
    'CONFIG',
    'CONFIG',
    'CONFIG',
    'CONTRACT_VERSION',
    'CONTRACT_VERSION',
    'CONTRACT_VERSION',
    'CONTRACT_VERSION',
    'EXAMPLES',
    'EXAMPLES',
    'EXAMPLES',
    'EXAMPLES',
    'MODEL',
    'MODEL',
    'MODEL',
    'MODEL',
    'MODEL_PATH',
    'SKILL_ID',
    'SKILL_ID',
    'SKILL_ID',
    'SKILL_ID',
    'SKILL_ID',
    'SKILL_ID',
    'SKILL_VERSION',
    'SKILL_VERSION',
    'SKILL_VERSION',
    'SKILL_VERSION',
    'SKILL_VERSION',
    'SKILL_VERSION',
    'SYMBOL',
    'SYMBOL',
    'SYMBOL',
    'SYMBOL',
    'TRAIN_PATH',
    'VERBS',
    'VERBS',
    'VERBS',
    'VERBS',
    'VERSION_PATH',
    '_template',
    'echo_skill',
    'math_divide_skill',
    'math_multiply_skill',
    'math_subtract_skill',
    'math_sum_skill',
    'sentiment_skill'
]
__version__ = '0.0.1'
