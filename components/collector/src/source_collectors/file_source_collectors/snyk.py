"""Snyk metrics collector."""

from datetime import datetime, timezone
from typing import Tuple

from dateutil.parser import parse

from collector_utilities.functions import md5_hash
from collector_utilities.type import Entities, Response, Responses, Value
from base_collectors import JSONFileSourceCollector, SourceUpToDatenessCollector


class SnykSecurityWarnings(JSONFileSourceCollector):
    """Snyk collector for security warnings."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities = []
        for response in responses:
            json = await response.json()
            vulnerabilities = json.get("vulnerabilities", []) if isinstance(json, dict) else []
            entities.extend([
                dict(
                    key=md5_hash(f'{vulnerability["title"]}:{vulnerability["packageName"]}'),
                    cve=vulnerability["title"],
                    package=vulnerability["packageName"],
                    severity=vulnerability["severity"],
                    version=vulnerability['version'],
                    package_include=" ➜ ".join([str(x) for x in vulnerability["from"][1:]]) if isinstance(vulnerability["from"], list) else vulnerability["from"],
                    fix=", ".join([str(x) for x in vulnerability["fixedIn"]]) if isinstance(vulnerability["fixedIn"], list) else vulnerability["fixedIn"],
                    url="https://snyk.io/vuln/" + vulnerability["id"])

                for vulnerability in vulnerabilities])
        sorted_entities = list({v['package']: v for v in entities}.values())
        return str(len(sorted_entities)), "100", sorted_entities


class SnykSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Snyk collector for source up-to-dateness."""

    API_URL_PARAMETER_KEY = "details_url"

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        details = await response.json()
        return parse(details[0]["analyzed_at"]) \
            if isinstance(details, list) and details and "analyzed_at" in details[0] else datetime.now(timezone.utc)
