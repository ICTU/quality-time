"""Generic metrics security warnings collector."""

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import md5_hash
from model import Entities, Entity, SourceResponses


class GenericJSONSecurityWarnings(JSONFileSourceCollector):
    """Generic collector for security warnings."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the JSON."""
        entities = Entities()
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
        return entities
