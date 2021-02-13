"""Anchore metrics collector."""

from datetime import datetime, timezone

from dateutil.parser import parse

from base_collectors import JSONFileSourceCollector, SourceUpToDatenessCollector
from collector_utilities.functions import md5_hash
from collector_utilities.type import Response
from source_model import Entity, SourceMeasurement, SourceResponses


class AnchoreSecurityWarnings(JSONFileSourceCollector):
    """Anchore collector for security warnings."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the Anchore security warnings."""
        severities = self._parameter("severities")
        entities = []
        for response in responses:
            json = await response.json(content_type=None)
            vulnerabilities = json.get("vulnerabilities", []) if isinstance(json, dict) else []
            entities.extend(
                [
                    Entity(
                        # Include the filename in the hash so that it is unique even when multiple images contain the
                        # same package with the same vulnerability. Don't add a colon so existing hashes stay the same
                        # if the source is not a zipped report (filename is an empty string in that case).
                        key=md5_hash(f'{response.filename}{vulnerability["vuln"]}:{vulnerability["package"]}'),
                        cve=vulnerability["vuln"],
                        filename=response.filename,
                        package=vulnerability["package"],
                        severity=vulnerability["severity"],
                        fix=vulnerability["fix"],
                        url=vulnerability["url"],
                    )
                    for vulnerability in vulnerabilities
                    if vulnerability["severity"] in severities
                ]
            )
        return SourceMeasurement(entities=entities)


class AnchoreSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Anchore collector for source up-to-dateness."""

    API_URL_PARAMETER_KEY = "details_url"

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the analysis date and time from the report."""
        details = await response.json(content_type=None)
        return (
            parse(details[0]["analyzed_at"])
            if isinstance(details, list) and details and "analyzed_at" in details[0]
            else datetime.now(timezone.utc)
        )
