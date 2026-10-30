"""Notification destination."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Destination:
    """Notification destination."""

    webhook: str
    report_url: str = ""  # The landing URL to include in notifications so users can navigate back to Quality-time

    @classmethod
    def from_dict(cls, destination: dict[str, str]) -> Destination:
        """Create a destination from the notification destination data of a report."""
        return cls(destination["webhook"], destination.get("report_url", "").strip("/"))
