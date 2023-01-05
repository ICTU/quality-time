"""cloc LOC collector."""

from collections import defaultdict

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import match_string_or_regular_expression
from model import Entities, Entity, SourceMeasurement, SourceResponses


class ClocLOC(JSONFileSourceCollector):
    """cloc collector for size/lines of code."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the LOC from the JSON responses."""
        # The JSON is produced by cloc --json or by cloc --by-file --json, so be prepared for both formats
        languages_to_ignore = self._parameter("languages_to_ignore")
        files_to_include = self._parameter("files_to_include")
        cloc_by_language: dict[str, dict[str, int]] = defaultdict(lambda: dict(nFiles=0, blank=0, comment=0, code=0))
        total = 0
        for response in responses:
            for key, value in (await response.json(content_type=None)).items():
                language = self.determine_language(key, value)
                if key in ("header", "SUM") or match_string_or_regular_expression(language, languages_to_ignore):
                    continue
                # Count the total LOC for all files so the user can measure the percentage of test code, for example.
                total += value["code"]
                filename = self.determine_filename(key, value)
                if filename and files_to_include and not match_string_or_regular_expression(filename, files_to_include):
                    continue
                for field, default_value in dict(blank=0, comment=0, code=0, nFiles=1).items():
                    cloc_by_language[language][field] += value.get(field, default_value)
        loc = sum(value["code"] for value in cloc_by_language.values())
        entities = Entities(self.create_entity(key, value) for key, value in cloc_by_language.items())
        return SourceMeasurement(value=str(loc), total=str(total), entities=entities)

    @staticmethod
    def create_entity(language: str, cloc: dict[str, int]) -> Entity:
        """Create an entity from a cloc programming language count."""
        return Entity(
            key=language,
            language=language,
            blank=str(cloc["blank"]),
            comment=str(cloc["comment"]),
            code=str(cloc["code"]),
            nr_files=str(cloc["nFiles"]),
        )

    @staticmethod
    def determine_language(key: str, value: dict[str, int | str]) -> str:
        """Return the language of the item."""
        return str(value.get("language", key))

    @staticmethod
    def determine_filename(key: str, value: dict[str, int | str]) -> str | None:
        """Return the filename of the item, if any."""
        return key if "language" in value else None
