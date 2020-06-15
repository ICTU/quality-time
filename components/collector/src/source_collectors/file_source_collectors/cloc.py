"""cloc metrics collector."""

from typing import Tuple

from collector_utilities.type import Entities, Responses, Value
from base_collectors import JSONFileSourceCollector


class ClocLOC(JSONFileSourceCollector):
    """cloc collector for size/lines of code."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        loc = 0
        entities = []
        for response in responses:
            for key, value in (await response.json()).items():
                if key not in ("header", "SUM"):
                    loc += value["code"]
                    entities.append(
                        dict(key=key, language=key, blank=str(value["blank"]), comment=str(value["comment"]),
                             code=str(value["code"]), nr_files=str(value["nFiles"])))
        return str(loc), str(loc), entities
