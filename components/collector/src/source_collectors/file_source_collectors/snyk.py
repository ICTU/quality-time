"""Snyk metrics collector."""

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import md5_hash
from source_model import SourceMeasurement, SourceResponses


class SnykSecurityWarnings(JSONFileSourceCollector):
    """Snyk collector for security warnings."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        entities = []
        severities = self._parameter("severities")
        for response in responses:
            json = await response.json(content_type=None)
            vulnerabilities = json.get("vulnerabilities", []) if isinstance(json, dict) else []
            for vulnerability in vulnerabilities:
                if vulnerability["severity"].lower() not in severities:
                    continue
                package_include = " ➜ ".join([str(package) for package in vulnerability["from"][1:]]) \
                    if isinstance(vulnerability["from"], list) else vulnerability["from"]
                fix = ", ".join([str(package) for package in vulnerability["fixedIn"]]) \
                    if isinstance(vulnerability["fixedIn"], list) else vulnerability["fixedIn"]
                key = md5_hash(f'{vulnerability["id"]}:{package_include}')
                entities.append(
                    dict(
                        key=key, cve=vulnerability["title"], package=vulnerability["packageName"],
                        severity=vulnerability["severity"], version=vulnerability['version'],
                        package_include=package_include, fix=fix, url=f"https://snyk.io/vuln/{vulnerability['id']}"))
        return SourceMeasurement(entities=entities)
