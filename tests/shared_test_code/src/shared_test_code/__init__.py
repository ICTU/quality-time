"""Shared test code, used by the unit tests of multiple components."""

import fnmatch
import functools
import logging
import pkgutil
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def disable_logging[**P, ReturnType](func: Callable[P, ReturnType]) -> Callable[P, ReturnType]:
    """Temporarily disable logging while the decorated function runs."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> ReturnType:
        """Disable logging before calling func and re-enable it afterwards."""
        logging.disable(logging.CRITICAL)
        try:
            return func(*args, **kwargs)
        finally:
            logging.disable(logging.NOTSET)

    return wrapper


def package_names(folder: str) -> list[str]:
    """Return the sorted names of the packages directly under the folder."""
    return sorted(module.name for module in pkgutil.iter_modules([folder]) if module.ispkg)


def path_glob(folder: str) -> re.Pattern[str]:
    """Compile a regular expression that matches all Python files under the folder, recursively.

    ArchUnitPython matches in_path() patterns with fnmatch, where "**/" is two stars followed by a
    required slash, so "folder/**/*.py" would not match a file directly in the folder such as
    "folder/foo.py". Also match the variant with the "**/" removed, reusing fnmatch's own translation,
    so that files directly in the folder are included too.
    """
    glob = f"{folder}/**/*.py"
    variants = {glob, glob.replace("**/", "")}
    return re.compile("|".join(fnmatch.translate(variant) for variant in variants))
