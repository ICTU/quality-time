"""Checkmarx CxSAST time passed collector."""

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Value
from model import SourceResponses

from .base import CxSASTScanBase


class CxSASTTimePassed(CxSASTScanBase):
    """Collector class to measure the time passed since the latest Checkmarx CxSAST scan."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the date and time of the most recent scan."""
        scan = (await responses[0].json())[0]
        return str(days_ago(parse(scan["dateAndTime"]["finishedOn"])))
