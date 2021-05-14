"""Robot Framework collector base classes."""

from abc import ABC
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from packaging.version import Version

from base_collectors import XMLFileSourceCollector
from collector_utilities.type import URL
from source_model import SourceResponses


class RobotFrameworkBaseClass(XMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Robot Framework collectors."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to change the filename."""
        url = str(await super()._landing_url(responses))
        return URL(url.replace("output.html", "report.html"))

    @staticmethod
    def _parse_version(tree: Element) -> Version:
        """Parse the version from the Robot Framework XML."""
        generator = tree.get("generator") or "Robot 0"
        # The generator field looks like: 'Robot 3.1.1 (Python 3.7.0 on darwin)'
        return Version(generator.split(" ")[1])
