"""Dependency-Track JSON types."""

from typing import NotRequired, TypedDict


class DependencyTrackMetrics(TypedDict, total=False):
    """Project metrics as returned by Dependency-Track."""

    # Last occurrence is a Unix timestamp of the datetime of the last BOM analysis
    lastOccurrence: int


class DependencyTrackProject(TypedDict):
    """Project as returned by Dependency-Track."""

    # Last BOM import is a Unix timestamp, despite the Dependency-Tracker Swagger docs saying it's a datetime string
    # See https://github.com/DependencyTrack/dependency-track/issues/840
    lastBomImport: int
    name: str
    uuid: str
    isLatest: NotRequired[bool]
    metrics: NotRequired[DependencyTrackMetrics]
    version: NotRequired[str]
