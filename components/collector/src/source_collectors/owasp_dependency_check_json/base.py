"""Base classes for OWASP Dependency-Check JSON collectors."""

from abc import ABC
from typing import ClassVar, TypedDict

from base_collectors import JSONFileSourceCollector
from collector_utilities.exceptions import JSONAttributeError


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


class OWASPDependencyCheckJSONBase(JSONFileSourceCollector, ABC):
    """Base class for OWASP Dependency-Check JSON collectors."""

    allowed_report_schemas: ClassVar[list[str]] = ["1.1"]

    def _check_report_schema(self, json: OWASPDependencyCheckJSON) -> None:
        """Check that the report schema is allowed."""
        if (schema := json.get("reportSchema", "")) not in self.allowed_report_schemas:
            raise JSONAttributeError(self.allowed_report_schemas, "reportSchema", schema)
