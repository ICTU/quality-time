"""Measurement model class."""

from typing import Optional, cast

from server_utilities.functions import iso_timestamp
from server_utilities.type import Scale, Status, TargetType


class Measurement(dict):
    """Class representing a measurement."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if "_id" in self:
            del self["_id"]
        self["start"] = self["end"] = iso_timestamp()

    def target(self, scale: Scale, target_type: TargetType) -> Optional[str]:
        """Return the measurement target value for the scale."""
        return cast(Optional[str], self.get(scale, {}).get(target_type))

    def status(self, scale: Scale) -> Optional[Status]:
        """Return the measurement status for the scale."""
        return cast(Optional[Status], self.get(scale, {}).get("status"))
