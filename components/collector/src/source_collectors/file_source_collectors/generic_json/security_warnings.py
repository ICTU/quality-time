"""Generic metrics security warnings collector."""

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import md5_hash
from source_model import Entity, SourceMeasurement, SourceResponses


class GenericJSONSecurityWarnings(JSONFileSourceCollector):
    """Generic collector for security warnings."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:  # skipcq: PY-D0003
        """Override to parse the security warnings from the JSON."""
        entities = []
        for response in responses:
            json = await response.json(content_type=None)
            vulnerabilities = json.get("vulnerabilities", [])
            for vulnerability in vulnerabilities:
                key = md5_hash(f'{vulnerability["title"]}:{vulnerability["description"]}')
                entities.append(
                    Entity(
                        key=key,
                        title=vulnerability["title"],
                        description=vulnerability["description"],
                        severity=vulnerability["severity"],
                    )
                )
        return SourceMeasurement(entities=entities)
