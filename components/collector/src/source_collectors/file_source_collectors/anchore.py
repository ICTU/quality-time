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
        severities = self._parameter("severities")
        entities = []
        for response in responses:
            json = await response.json(content_type=None)
            vulnerabilities = json.get("vulnerabilities", []) if isinstance(json, dict) else []
            entities.extend([
                Entity(
                    key=md5_hash(f'{vulnerability["vuln"]}:{vulnerability["package"]}'),
                    cve=vulnerability["vuln"],
                    package=vulnerability["package"],
                    severity=vulnerability["severity"],
                    fix=vulnerability["fix"],
                    url=vulnerability["url"])
                for vulnerability in vulnerabilities if vulnerability["severity"] in severities])
        return SourceMeasurement(entities=entities)


class AnchoreSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Anchore collector for source up-to-dateness."""

    API_URL_PARAMETER_KEY = "details_url"

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        details = await response.json(content_type=None)
        return parse(details[0]["analyzed_at"]) \
            if isinstance(details, list) and details and "analyzed_at" in details[0] else datetime.now(timezone.utc)
