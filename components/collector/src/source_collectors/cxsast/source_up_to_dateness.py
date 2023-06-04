"""Checkmarx CxSAST source up-to-dateness collector."""

from collector_utilities.date_time import days_ago, parse_datetime
from collector_utilities.type import Value
from model import SourceResponses

from .base import CxSASTScanBase


class CxSASTSourceUpToDateness(CxSASTScanBase):
    """Collector class to measure the up-to-dateness of a Checkmarx CxSAST scan."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the date and time of the most recent scan."""
        scan = (await responses[0].json())[0]
        return str(days_ago(parse_datetime(scan["dateAndTime"]["finishedOn"])))
