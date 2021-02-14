"""Checkmarx CxSAST source up-to-dateness collector."""

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from source_model import SourceMeasurement, SourceResponses

from .base import CxSASTBase


class CxSASTSourceUpToDateness(CxSASTBase):
    """Collector class to measure the up-to-dateness of a Checkmarx CxSAST scan."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the date and time of the most recent scan."""
        scan = (await responses[0].json())[0]
        return SourceMeasurement(value=str(days_ago(parse(scan["dateAndTime"]["finishedOn"]))))
