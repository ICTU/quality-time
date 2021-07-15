"""cloc LOC collector."""

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import match_string_or_regular_expression
from model import Entities, Entity, SourceMeasurement, SourceResponses


class ClocLOC(JSONFileSourceCollector):
    """cloc collector for size/lines of code."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the LOC from the JSON responses."""
        loc = 0
        entities = Entities()
        languages_to_ignore = self._parameter("languages_to_ignore")
        for response in responses:
            for key, value in (await response.json(content_type=None)).items():
                if key not in ("header", "SUM") and not match_string_or_regular_expression(key, languages_to_ignore):
                    loc += value["code"]
                    entities.append(
                        Entity(
                            key=key,
                            language=key,
                            blank=str(value["blank"]),
                            comment=str(value["comment"]),
                            code=str(value["code"]),
                            nr_files=str(value["nFiles"]),
                        )
                    )
        return SourceMeasurement(value=str(loc), entities=entities)
