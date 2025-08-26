"""Trivy JSON types."""

from typing import NotRequired, TypedDict

# The types below are based on https://aquasecurity.github.io/trivy/v0.45/docs/configuration/reporting/#json.
# That documentation says: "VulnerabilityID, PkgName, InstalledVersion, and Severity in Vulnerabilities are always
# filled with values, but other fields might be empty." This unfortunately does not tell us whether empty means
# an empty string or null. It's also unclear whether keys may be missing. For now we assume all keys are always
# present and missing values are empty strings.


class TrivyJSONVulnerability(TypedDict):
    """Trivy JSON for one vulnerability."""

    VulnerabilityID: str
    Title: NotRequired[str]
    Description: NotRequired[str]
    Severity: str
    PkgName: str
    InstalledVersion: str
    FixedVersion: NotRequired[str]
    References: NotRequired[list[str]]


class TrivyJSONResult(TypedDict):
    """Trivy JSON for one dependency repository."""

    Target: str
    Vulnerabilities: NotRequired[list[TrivyJSONVulnerability]]  # Examples in the Trivy docs show this key can be null


# Trivy JSON reports come in two different forms, following schema version 1 or schema version 2.
# Schema version 1 is not explicitly documented as a schema. The Trivy docs only give an example report.
# See https://aquasecurity.github.io/trivy/v0.55/docs/configuration/reporting/#json.
# Schema version 2 is not explicitly documented as a schema either. The only thing available seems to be a GitHub
# discussion: https://github.com/aquasecurity/trivy/discussions/1050.

TriviJSONSchemaVersion1 = list[TrivyJSONResult]


class TrivyJSONSchemaVersion2(TypedDict):
    """Trivy JSON conform schema version 2."""

    SchemaVersion: int
    Results: list[TrivyJSONResult]


TrivyJSON = TriviJSONSchemaVersion1 | TrivyJSONSchemaVersion2
