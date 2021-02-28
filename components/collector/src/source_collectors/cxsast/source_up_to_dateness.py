"""Checkmarx CxSAST source up-to-dateness collector."""

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Value
from source_model import SourceResponses

from .base import CxSASTBase


class CxSASTSourceUpToDateness(CxSASTBase):
    """Collector class to measure the up-to-dateness of a Checkmarx CxSAST scan."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the date and time of the most recent scan."""
        scan = (await responses[0].json())[0]
        return str(days_ago(parse(scan["dateAndTime"]["finishedOn"])))
