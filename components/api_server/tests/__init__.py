"""Initialize the environment for the unit tests."""

import sys

from shared.utils.env import loadenv

loadenv("default.env")

sys.path.append("../shared_code/tests")
