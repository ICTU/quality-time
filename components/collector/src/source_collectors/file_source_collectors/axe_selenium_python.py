"""axe-selenium-python accessibility analysis metric source."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import JSONFileSourceCollector, SourceUpToDatenessCollector
from collector_utilities.functions import md5_hash
from collector_utilities.type import Response
from source_model import Entity, SourceMeasurement, SourceResponses


class AxeSeleniumPythonAccessibility(JSONFileSourceCollector):
    """Collector class to get accessibility violations."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        impact_levels = self._parameter("impact")
        entity_attributes = []
        for response in responses:
            json = await response.json(content_type=None)
            url = json["url"]
            for violation in json.get("violations", []):
                for node in violation.get("nodes", []):
                    if node.get("impact") not in impact_levels:
                        continue
                    entity_attributes.append(
                        dict(
                            description=violation.get("description"),
                            element=node.get("html"),
                            help=violation.get("helpUrl"),
                            impact=node.get("impact"),
                            page=url,
                            url=url,
                            tags=", ".join(sorted(violation.get("tags", []))),
                            violation_type=violation.get("id"),
                        )
                    )
        entities = [
            Entity(
                key=md5_hash(",".join(str(value) for key, value in attributes.items() if key != "tags")), **attributes
            )
            for attributes in entity_attributes
        ]
        return SourceMeasurement(entities=entities)


class AxeSeleniumPythonSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to get the source up-to-dateness of axe-selenium-python JSON reports."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return parse((await response.json(content_type=None))["timestamp"])
