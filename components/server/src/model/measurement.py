"""Measurement model class."""

from typing import Optional, cast

from server_utilities.functions import iso_timestamp
from server_utilities.type import Scale, Status, TargetType


class Measurement(dict):
    """Class representing a measurement."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if "_id" in self:
            del self["_id"]  # Remove the Mongo ID if present so this measurement can be re-inserted in the database.
        self["start"] = self["end"] = iso_timestamp()

    def target(self, scale: Scale, target_type: TargetType) -> Optional[str]:
        """Return the measurement target value for the scale."""
        return cast(Optional[str], self.get(scale, {}).get(target_type))

    def status(self, scale: Scale) -> Optional[Status]:
        """Return the measurement status for the scale."""
        return cast(Optional[Status], self.get(scale, {}).get("status"))

    def status_start(self, scale: Scale) -> Optional[str]:
        """Return the start date of the status."""
        return str(self.get(scale, {}).get("status_start", "")) or None

    def set_status_start(self, scale: Scale, previous_measurement: "Measurement") -> None:
        """Set the status start date."""
        current_status = self.status(scale)
        previous_status = previous_measurement.status(scale)
        status_start = previous_measurement.status_start(scale) if current_status == previous_status else self["start"]
        if status_start:
            self[scale]["status_start"] = status_start
