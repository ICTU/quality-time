"""Base classes for Jira collectors."""

from typing import cast

from collector_utilities.type import URL, Value
from model import Entities, Entity

from .issues import JiraIssues


class JiraFieldSumBase(JiraIssues):
    """Base class for collectors that sum a custom Jira field."""

    field_parameter = "subclass responsibility"
    entity_key = "subclass responsibility"

    @classmethod
    def _compute_value(cls, entities: Entities) -> Value:
        """Override to sum the field, as specified by the entity key, from the entities."""
        return str(round(sum(float(entity[cls.entity_key]) for entity in entities)))

    def _create_entity(self, issue: dict, url: URL) -> Entity:
        """Extend to also add the summed field to the entity."""
        entity = super()._create_entity(issue, url)
        entity[self.entity_key] = str(cast(float, self.__value_of_field_to_sum(issue)))
        return entity

    def _include_issue(self, issue: dict) -> bool:
        """Override to only include issues that have a sum."""
        return self.__value_of_field_to_sum(issue) is not None

    def _fields(self) -> str:
        """Extend to also get the field this collector needs to sum."""
        return super()._fields() + "," + cast(str, self._parameter(self.field_parameter))

    def __value_of_field_to_sum(self, issue: dict) -> float | None:
        """Return the value of the issue field that this collector is to sum."""
        value = issue["fields"].get(self._parameter(self.field_parameter))
        return value if value is None else float(value)
