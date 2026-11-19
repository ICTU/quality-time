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
    lastBomImport: NotRequired[int]
    name: str
    uuid: str
    isLatest: NotRequired[bool]
    metrics: NotRequired[DependencyTrackMetrics]
    version: NotRequired[str]


class DependencyTrackRepositoryMetaData(TypedDict):
    """Repository meta data as returned by Dependency-Track."""

    latestVersion: str


class DependencyTrackResolvedLicense(TypedDict):
    """License of a component as returned by Dependency-Track, with only the attributes the collector needs."""

    name: str
    uuid: str
    licenseId: NotRequired[str]  # The SPDX license identifier, absent for custom licenses


class DependencyTrackLicenseGroup(TypedDict):
    """License group as returned by Dependency-Track."""

    name: str


class DependencyTrackLicense(TypedDict):
    """License as returned by the Dependency-Track license API."""

    name: str
    uuid: str
    licenseId: NotRequired[str]
    isOsiApproved: NotRequired[bool]
    isFsfLibre: NotRequired[bool]
    isDeprecatedLicenseId: NotRequired[bool]
    licenseGroups: NotRequired[list[DependencyTrackLicenseGroup]]


class DependencyTrackComponent(TypedDict):
    """Component as returned by the Dependency-Track component API, with only the attributes the collector needs."""

    name: str
    uuid: str
    # Direct dependencies is a JSON string with a list of component identities, and null if the component has none
    directDependencies: NotRequired[str | None]
    license: NotRequired[str]  # License name, if Dependency-Track could not resolve the license
    repositoryMeta: NotRequired[DependencyTrackRepositoryMetaData]
    resolvedLicense: NotRequired[DependencyTrackResolvedLicense]
    version: NotRequired[str]
