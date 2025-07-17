"""Robot Framework collector base classes."""

from abc import ABC
from typing import TYPE_CHECKING

from base_collectors import XMLFileSourceCollector
from collector_utilities.type import URL

if TYPE_CHECKING:
    from model import SourceResponses


class RobotFrameworkBaseClass(XMLFileSourceCollector, ABC):
    """Base class for Robot Framework collectors."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to change the filename."""
        url = str(await super()._landing_url(responses))
        return URL(url.replace("output.html", "report.html"))
