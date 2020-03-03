"""Anchore metrics collector."""

from datetime import datetime, timezone
from typing import Tuple

from dateutil.parser import parse

from collector_utilities.functions import md5_hash
from collector_utilities.type import Entities, Response, Responses, Value
from .source_collector import JSONFileSourceCollector, SourceUpToDatenessCollector


class AnchoreSecurityWarnings(JSONFileSourceCollector):
    """Anchore collector for security warnings."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        severities = self._parameter("severities")
        entities = []
        for response in responses:
            json = response.json()
            vulnerabilities = json.get("vulnerabilities", []) if isinstance(json, dict) else []
            entities.extend([
                dict(
                    key=md5_hash(f'{vulnerability["vuln"]}:{vulnerability["package"]}'),
                    cve=vulnerability["vuln"],
                    package=vulnerability["package"],
                    severity=vulnerability["severity"],
                    fix=vulnerability["fix"],
                    url=vulnerability["url"])
                for vulnerability in vulnerabilities if vulnerability["severity"] in severities])
        return str(len(entities)), "100", entities


class AnchoreSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Anchore collector for source up-to-dateness."""

    API_URL_PARAMETER_KEY = "details_url"

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        details = response.json()
        return parse(details[0]["analyzed_at"]) \
            if isinstance(details, list) and details and "analyzed_at" in details[0] else datetime.now(timezone.utc)
