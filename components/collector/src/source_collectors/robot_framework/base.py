"""Robot Framework collector base classes."""

from abc import ABC

from base_collectors import XMLFileSourceCollector
from collector_utilities.type import URL
from model import SourceResponses


class RobotFrameworkBaseClass(XMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Robot Framework collectors."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to change the filename."""
        url = str(await super()._landing_url(responses))
        return URL(url.replace("output.html", "report.html"))
