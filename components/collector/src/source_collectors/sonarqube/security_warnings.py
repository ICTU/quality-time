"""SonarQube security warnings collector."""

from .violations import SonarQubeViolations


class SonarQubeSecurityWarnings(SonarQubeViolations):
    """SonarQube security warnings, which basically are issues with security impact."""

    def _url_parameters(self) -> str:
        """Override to return parameters needed for issues with security impact, common to API URL and landing URL."""
        return (
            self._query_parameter("impact_severities", uppercase=True)
            + "&impactSoftwareQualities=SECURITY"
            + self._query_parameter("tags")
        )
