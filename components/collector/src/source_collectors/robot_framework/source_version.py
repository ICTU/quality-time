"""Robot Framework source version collector."""

from packaging.version import Version

from base_collectors import SourceVersionCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response

from .base import RobotFrameworkBaseClass


class RobotFrameworkSourceVersion(RobotFrameworkBaseClass, SourceVersionCollector):
    """Collector to collect the Robot Framework version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the Robot Framework XML."""
        return self._parse_version(await parse_source_response_xml(response))
