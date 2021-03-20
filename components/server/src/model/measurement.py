"""Measurement model class."""

from collections.abc import Sequence
from typing import Optional, cast

from server_utilities.functions import iso_timestamp
from server_utilities.type import Scale, Status, TargetType


class Source(dict):
    """Class representing a measurement source."""

    def ignored_entity_keys(self) -> Sequence[str]:
        """Return the keys of the ignored entities."""
        entities = self.get("entity_user_data", {}).items()
        return [entity[0] for entity in entities if entity[1].get("status") in ("fixed", "false_positive", "wont_fix")]


class Measurement(dict):
    """Class representing a measurement."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self["start"] = self["end"] = iso_timestamp()

    def copy(self) -> "Measurement":
        """Extend to return an instance of this class instead of a dict."""
        return self.__class__(super().copy())

    def set_target(self, scale: Scale, target_type: TargetType, value: Optional[str]) -> None:
        """Set the specified target for the scale."""
        self.setdefault(scale, {})[target_type] = value

    def status(self, scale: Scale) -> Optional[Status]:
        """Return the measurement status for the scale."""
        return cast(Optional[Status], self.get(scale, {}).get("status"))

    def set_status(self, scale: Scale, status: Optional[str], previous_measurement: "Measurement") -> None:
        """Set the measurement status for the scale and the status start date."""
        self.setdefault(scale, {})["status"] = status
        previous_status = previous_measurement.status(scale)
        status_start = previous_measurement.status_start(scale) if status == previous_status else self["start"]
        if status_start:
            self[scale]["status_start"] = status_start

    def status_start(self, scale: Scale) -> Optional[str]:
        """Return the start date of the status."""
        return str(self.get(scale, {}).get("status_start", "")) or None

    def sources(self) -> Sequence[Source]:
        """Return the measurement's sources."""
        return [Source(source) for source in self["sources"]]
