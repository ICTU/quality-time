"""Bandit metrics collector."""

from datetime import datetime

from dateutil.parser import parse

from collector_utilities.type import Response, Responses
from base_collectors import JSONFileSourceCollector, SourceMeasurement, SourceUpToDatenessCollector


class BanditSecurityWarnings(JSONFileSourceCollector):
    """Bandit collector for security warnings."""

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        severities = self._parameter("severities")
        confidence_levels = self._parameter("confidence_levels")
        entities = []
        for response in responses:
            entities.extend([
                dict(
                    key=f'{warning["test_id"]}:{warning["filename"]}:{warning["line_number"]}',
                    location=f'{warning["filename"]}:{warning["line_number"]}',
                    issue_text=warning["issue_text"],
                    issue_severity=warning["issue_severity"].capitalize(),
                    issue_confidence=warning["issue_confidence"].capitalize(),
                    more_info=warning["more_info"])
                for warning in (await response.json(content_type=None)).get("results", [])
                if warning["issue_severity"].lower() in severities
                and warning["issue_confidence"].lower() in confidence_levels])
        return SourceMeasurement(entities=entities)


class BanditSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Bandit collector for source up-to-dateness."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return parse((await response.json(content_type=None))["generated_at"])
