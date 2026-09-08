"""Entity user data model class."""

from typing import ClassVar, TYPE_CHECKING

from shared.model.entity_user_data import EntityUserData as SharedEntityUserData

from utils.functions import sanitize_html

if TYPE_CHECKING:
    from .report import Report


class EntityUserData(SharedEntityUserData):
    """Subclass the shared entity user data class to add methods specific for the API-server."""

    # The entity user data attributes that users can set. Other attributes are either derived from these or
    # maintained by Quality-time itself, so they cannot be set through the API:
    SETTABLE_ATTRIBUTES: ClassVar[tuple[str, ...]] = ("status", "status_end_date", "rationale")

    def set_attribute(self, attribute: str, value: str, entity_description: str, report: Report) -> str:
        """Set the attribute of the entity, and the attributes derived from it, and describe the changes."""
        if attribute == "rationale" and value:
            value = sanitize_html(value)  # The frontend renders the rationale as HTML
        old_value = self.get(attribute) or ""
        self[attribute] = value
        description = f"changed the {attribute} of '{entity_description}' from '{old_value}' to '{value}'"
        description += self._set_derived_attributes(attribute, value, report)
        self.set_exclusion_attributes()
        return description

    def _set_derived_attributes(self, attribute: str, value: str, report: Report) -> str:
        """Set the attributes derived from the attribute that was just set, and describe the changes."""
        if attribute != "status":
            return ""
        old_status_end_date = self.get("status_end_date")
        new_status_end_date = report.deadline(value)
        if new_status_end_date == old_status_end_date:
            return ""
        self["status_end_date"] = new_status_end_date
        return f" and changed the status end date from '{old_status_end_date}' to '{new_status_end_date}'"
