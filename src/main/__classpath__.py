#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Project classpath bootstrapper."""

import warnings
from pathlib import Path

from hspylib.core.metaclass.classpath import Classpath
from hspylib.core.tools.commons import is_debugging, parent_path

if not is_debugging():
    warnings.simplefilter("ignore", category=FutureWarning)
    warnings.simplefilter("ignore", category=UserWarning)
    warnings.simplefilter("ignore", category=DeprecationWarning)
    warnings.simplefilter("ignore", category=UserWarning)


class _Classpath(Classpath):
    """Manage classpath paths for the project.
    :return: None.
    """

    def __init__(self):
        """  init  .
        :return: None.
        """
        source_root: Path = parent_path(__file__)
        project_root: Path = parent_path(str(parent_path(str(source_root))))
        super().__init__(source_root, project_root, (source_root / "resources"))


# Instantiate the classpath singleton for global access.
assert (classpath := _Classpath()) is not None, "Failed to create Classpath instance"
