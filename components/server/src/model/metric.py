"""Metric model class."""

from collections.abc import Sequence
from datetime import date
from typing import Optional, cast

from server_utilities.type import Direction, Scale, Status, TargetType


class Metric:
    """Class representing a metric."""

    def __init__(self, data_model, metric_data) -> None:
        self.__data_model = data_model
        self.__data = metric_data

    def type(self) -> str:
        """Return the type of the metric."""
        return str(self.__data["type"])

    def addition(self):
        """Return the addition operator of the metric: sum, min, or max."""
        return dict(max=max, min=min, sum=sum)[self.__data["addition"]]

    def direction(self) -> Direction:
        """Return the direction of the metric: < or >."""
        return cast(Direction, self.__data.get("direction") or self.__data_model["metrics"][self.type()]["direction"])

    def scale(self) -> Scale:
        """Return the current metric scale."""
        return cast(Scale, self.__data.get("scale", "count"))

    def scales(self) -> Sequence[Scale]:
        """Return the current metric's supported scales."""
        return cast(Sequence[Scale], self.__data_model["metrics"][self.type()]["scales"])

    def accept_debt(self) -> bool:
        """Return whether the metric has its technical debt accepted."""
        return bool(self.__data.get("accept_debt", False))

    def accept_debt_expired(self) -> bool:
        """Return whether the accepted debt has expired."""
        return not self.accept_debt() or date.today().isoformat() > self.debt_end_date()

    def debt_end_date(self) -> str:
        """Return the end date of the accepted technical debt."""
        return str(self.__data.get("debt_end_date")) or date.max.isoformat()

    def target(self) -> float:
        """Return the metric target value."""
        return float(
            self.__data.get("target", self.__data_model.get("metric", {}).get(self.type(), {}).get("target")) or 0
        )

    def near_target(self) -> float:
        """Return the metric near target value."""
        return float(self.__data.get("near_target") or 0)

    def debt_target(self) -> float:
        """Return the metric debt target value."""
        return float(self.__data.get("debt_target") or 0)

    def get_target(self, target_type: TargetType) -> Optional[str]:
        """Return the target."""
        target = self.__data.get(target_type)
        return str(target) if target else None

    def status(self, measurement_value: Optional[str]) -> Optional[Status]:
        """Return the metric status, given a measurement value."""
        if measurement_value is None:
            # Allow for accepted debt if there is no measurement yet so that the fact that a metric does not have a
            # source can be accepted as technical debt
            return None if self.accept_debt_expired() or self.sources() else "debt_target_met"
        value = float(measurement_value)
        better_or_equal = {">": float.__ge__, "<": float.__le__}[self.direction()]
        if better_or_equal(value, self.target()):
            status: Status = "target_met"
        elif better_or_equal(value, self.debt_target()) and not self.accept_debt_expired():
            status = "debt_target_met"
        elif better_or_equal(self.target(), self.near_target()) and better_or_equal(value, self.near_target()):
            status = "near_target_met"
        else:
            status = "target_not_met"
        return status

    def sources(self) -> dict:
        """Return the metric sources."""
        return cast(dict, self.__data.get("sources", {}))
