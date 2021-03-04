"""SonarQube LOC collector."""

from collector_utilities.functions import match_string_or_regular_expression
from source_model import Entities, Entity

from .base import SonarQubeMetricsBaseClass


class SonarQubeLOC(SonarQubeMetricsBaseClass):
    """SonarQube lines of code."""

    LANGUAGES = dict(
        abap="ABAP",
        apex="Apex",
        c="C",
        cs="C#",
        cpp="C++",
        cobol="COBOL",
        css="CSS",
        flex="Flex",
        go="Go",
        web="HTML",
        jsp="JSP",
        java="Java",
        js="JavaScript",
        kotlin="Kotlin",
        objc="Objective-C",
        php="PHP",
        plsql="PL/SQL",
        py="Python",
        ruby="Ruby",
        scala="Scala",
        swift="Swift",
        tsql="T-SQL",
        ts="TypeScript",
        vbnet="VB.NET",
        xml="XML",
    )  # https://sonarcloud.io/api/languages/list

    def _value_key(self) -> str:
        """Override to return the type of lines to count."""
        return str(self._parameter("lines_to_count"))  # Either "lines" or "ncloc"

    def _metric_keys(self) -> str:
        """Extend to also return the language distribution metric key if the user wants to measure ncloc."""
        metric_keys = super()._metric_keys()
        if self._value_key() == "ncloc":
            metric_keys += ",ncloc_language_distribution"  # Also get the ncloc per language
        return metric_keys

    def _value(self, metrics: dict[str, str]) -> str:
        """Extend to only count selected languages if the user wants to measure ncloc."""
        if self._value_key() == "ncloc":
            # Our user picked non-commented lines of code (ncloc), so we can sum the ncloc per language, skipping
            # languages the user wants to ignore
            return str(sum(int(ncloc) for _, ncloc in self.__language_ncloc(metrics)))
        return super()._value(metrics)

    async def _entities(self, metrics: dict[str, str]) -> Entities:
        """Extend to return ncloc per language, if the users picked ncloc to measure."""
        if self._value_key() == "ncloc":
            # Our user picked non-commented lines of code (ncloc), so we can show the ncloc per language, skipping
            # languages the user wants to ignore
            return Entities(
                Entity(key=language, language=self.LANGUAGES.get(language, language), ncloc=ncloc)
                for language, ncloc in self.__language_ncloc(metrics)
            )
        return await super()._entities(metrics)

    def __language_ncloc(self, metrics: dict[str, str]) -> list[list[str]]:
        """Return the languages and non-commented lines of code per language, ignoring languages if so specified."""
        languages_to_ignore = [language.lower() for language in self._parameter("languages_to_ignore")]
        keys_to_ignore = [key for key, language in self.LANGUAGES.items() if language.lower() in languages_to_ignore]
        return [
            language_count.split("=")
            for language_count in metrics["ncloc_language_distribution"].split(";")
            if not match_string_or_regular_expression(language_count.split("=")[0], keys_to_ignore)
        ]
