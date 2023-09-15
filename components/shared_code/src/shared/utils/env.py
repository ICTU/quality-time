"""Environment functions."""

import os

from dotenv import load_dotenv


def getenv(key: str) -> str:
    """Return the environment variable's value as string."""
    return os.getenv(key, "")


def loadenv(*filenames: str) -> None:
    """Load the environment variables from the files.

    By default, load_dotenv doesn't override existing environment variables so pass file with the defaults last.
    """
    for filename in filenames:
        load_dotenv(filename)
