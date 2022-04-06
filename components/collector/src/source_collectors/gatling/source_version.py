"""Gatling source version collector."""

from packaging.version import Version

from base_collectors import SourceVersionCollector
from collector_utilities.type import Response

from .base import GatlingLogCollector


class GatlingSourceVersion(GatlingLogCollector, SourceVersionCollector):
    """Collector to collect the Gatling version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the XML."""
        text = await response.text()
        for line in text.splitlines():
            words = line.strip().split()
            if words[0] == "RUN":
                version_number_text = words[-1]  # Version number is the last string on the line that starts with RUN
                break
        else:
            version_number_text = "0"
        return Version(version_number_text)
