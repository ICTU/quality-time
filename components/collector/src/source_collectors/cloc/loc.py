"""cloc LOC collector."""

from collections import defaultdict

from base_collectors import JSONFileSourceCollector
from model import Entities, Entity, SourceMeasurement, SourceResponses


class ClocLOC(JSONFileSourceCollector):
    """cloc collector for size/lines of code."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the LOC from the JSON responses."""
        # The JSON is produced by cloc --json or by cloc --by-file --json, so be prepared for both formats
        cloc_by_language: dict[str, dict[str, int]] = defaultdict(
            lambda: {"nFiles": 0, "blank": 0, "comment": 0, "code": 0},
        )
        total = 0
        for response in responses:
            for key, value in (await response.json(content_type=None)).items():
                if key in ("header", "SUM"):
                    continue
                language = self.determine_language(key, value)
                if not self._matches_filter(language, exclude_parameter="languages_to_ignore"):
                    continue
                # Count the total LOC for all files so the user can use the percentage scale, for example
                # to measure the percentage of test code.
                total += value["code"]
                filename = self.determine_filename(key, value)
                if filename and not self._matches_filter(filename, "files_to_include"):
                    continue
                self._add_counts(cloc_by_language[language], value)
        loc = sum(value["code"] for value in cloc_by_language.values())
        entities = Entities(self.create_entity(key, value, loc) for key, value in cloc_by_language.items())
        return SourceMeasurement(value=str(loc), total=str(total), entities=entities)

    @staticmethod
    def _add_counts(language_counts: dict[str, int], value: dict[str, int]) -> None:
        """Add the blank, comment, code, and file counts of the value to the per-language counts."""
        for field, default_value in {"blank": 0, "comment": 0, "code": 0, "nFiles": 1}.items():
            language_counts[field] += value.get(field, default_value)

    @staticmethod
    def create_entity(language: str, cloc: dict[str, int], total: int) -> Entity:
        """Create an entity from a cloc programming language count."""
        return Entity(
            key=language,
            language=language,
            blank=str(cloc["blank"]),
            comment=str(cloc["comment"]),
            code=str(cloc["code"]),
            code_percentage=str(round(cloc["code"] / total * 100)),
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
