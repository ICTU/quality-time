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
        generator = (await parse_source_response_xml(response)).get("generator") or "Robot 0"
        # The generator field looks like: 'Robot 3.1.1 (Python 3.7.0 on darwin)'
        return Version(generator.split(" ")[1])
