"""Quality-time specific types."""

from typing import NewType, Union


Change = dict[str, Union[str, dict[str, str]]]
SessionId = NewType("SessionId", str)
