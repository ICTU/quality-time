"""Quality-time specific types."""

from typing import Any, NewType

JSON = dict[str, Any]
URL = NewType("URL", str)
