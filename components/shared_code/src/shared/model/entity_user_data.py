"""Entity user data model class."""

from datetime import datetime, timedelta
from typing import ClassVar, cast

from shared.utils.functions import iso_timestamp


class EntityUserData(dict):
    """Class representing the data that users can add to one measurement source entity.

    The user data consists of the status of the entity, the optional end date of that status, and the optional
    rationale for the status. In addition, the user data keeps track of when the entity disappeared from the
    measurement, if applicable, so that user data of entities that stay away can eventually be removed.
    """

    STATUSES_TO_IGNORE: ClassVar[tuple[str, ...]] = ("fixed", "false_positive", "wont_fix")
    # Keep user data of entities that disappeared from the measurement around for a while, in case they return:
    MAX_TIMEDELTA_TO_KEEP_ORPHANED: ClassVar[timedelta] = timedelta(days=21)

    @property
    def status(self) -> str | None:
        """Return the status of the entity, as set by the user."""
        return self.get("status")

    @property
    def rationale(self) -> str:  # pragma: no feature-test-cover
        """Return the rationale the user gave for the status of the entity."""
        return cast(str, self.get("rationale", ""))

    def is_ignored(self) -> bool:
        """Return whether to ignore the entity when calculating the measurement value.

        Prefer the exclusion attributes over the status attributes, and fall back to the status attributes for
        entity user data that has not been translated yet, see https://github.com/ICTU/quality-time/issues/9856.
        """
        if "excluded" in self:
            return bool(self["excluded"]) and not self._end_date_has_passed("exclusion_end_date")
        return self.status in self.STATUSES_TO_IGNORE and not self._end_date_has_passed("status_end_date")

    def _end_date_has_passed(self, attribute: str) -> bool:
        """Return whether the end date stored in the attribute has passed."""
        if end_date := self.get(attribute):
            end_datetime = datetime.fromisoformat(end_date)
            return end_datetime < datetime.now(tz=end_datetime.tzinfo)
        return False

    def set_exclusion_attributes(self) -> None:
        """Derive the exclusion attributes from the status attributes.

        The exclusion attributes will replace the status attributes, see
        https://github.com/ICTU/quality-time/issues/9856. They are maintained ahead of the user interface, which
        still uses the status attributes.
        """
        self["excluded"] = excluded = self.status in self.STATUSES_TO_IGNORE
        if excluded and (status_end_date := self.get("status_end_date")):
            self["exclusion_end_date"] = status_end_date
        else:
            self.pop("exclusion_end_date", None)

    def translate_legacy_attributes(self) -> None:  # pragma: no feature-test-cover
        """Add the exclusion attributes to entity user data that only has status attributes.

        The status attributes are kept, because the user interface still uses them. When the user interface starts
        using the exclusion attributes, the name of the status also needs to be translated into a rationale, so that
        the information the status carries is not lost.
        """
        if "excluded" not in self:  # If the entity user data has the exclusion attributes, it has been translated
            self.set_exclusion_attributes()

    def is_orphaned(self) -> bool:  # pragma: no feature-test-cover
        """Return whether the entity that this user data belongs to has disappeared from the measurement."""
        return "orphaned_since" in self

    def orphaned_too_long(self) -> bool:  # pragma: no feature-test-cover
        """Return whether the entity has been away for too long to keep its user data."""
        orphaned_since = datetime.fromisoformat(self["orphaned_since"])
        return datetime.now(tz=orphaned_since.tzinfo) - orphaned_since > self.MAX_TIMEDELTA_TO_KEEP_ORPHANED

    def mark_orphaned(self) -> None:  # pragma: no feature-test-cover
        """Record that the entity has disappeared from the measurement, as of now."""
        self["orphaned_since"] = iso_timestamp()

    def mark_not_orphaned(self) -> None:  # pragma: no feature-test-cover
        """Record that the entity is part of the measurement again."""
        self.pop("orphaned_since", None)
