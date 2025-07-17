"""Jenkins JSON types."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence


class Build(TypedDict):
    """Jenkins build."""

    duration: int
    result: str
    timestamp: int
    url: str


class Job(TypedDict):
    """Jenkins job."""

    buildable: bool
    builds: Sequence[Build]
    jobs: Sequence[Job]
    name: str
    url: str
