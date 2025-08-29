"""Jira JSON types."""

from typing import TypedDict


class Board(TypedDict):
    """Type for Jira boards."""

    id: int
    name: str
