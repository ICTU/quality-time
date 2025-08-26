"""Harbor JSON types."""

from typing import Final, TypedDict

REPORT_MIME_TYPE: Final = "application/vnd.security.vulnerability.report; version=1.1"


class HarborJSONVulnerability(TypedDict):
    """A Harbor JSON vulnerability."""

    id: str
    package: str
    version: str
    fix_version: str
    severity: str
    description: str
    links: list[str]


class HarborJSONVulnerabilityReport(TypedDict):
    """A Harbor JSON vulnerability report."""

    generated_at: str
    vulnerabilities: list[HarborJSONVulnerability]


HarborJSON = TypedDict(
    "HarborJSON",
    {"application/vnd.security.vulnerability.report; version=1.1": HarborJSONVulnerabilityReport},
)
