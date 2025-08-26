"""Types for OWASP Dependency-Check JSON."""

from typing import TypedDict


class Vulnerability(TypedDict):
    """OWASP Dependency-Check JSON vulnerability."""

    severity: str


class Dependency(TypedDict):
    """OWASP Dependency-Check JSON Dependency."""

    fileName: str
    filePath: str
    sha1: str
    vulnerabilities: list[Vulnerability]


class ScanInfo(TypedDict):
    """OWASP Dependency-Check JSON scan info."""

    engineVersion: str


class ProjectInfo(TypedDict):
    """OWASP Dependency-Check JSON project info."""

    reportDate: str


class OWASPDependencyCheckJSON(TypedDict):
    """OWASP Dependency-Check JSON format."""

    dependencies: list[Dependency]
    projectInfo: ProjectInfo
    reportSchema: str
    scanInfo: ScanInfo
