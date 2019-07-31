"""Shared measurement functions."""

from datetime import date
from typing import Optional


def calculate_measurement_value(sources, addition: str) -> Optional[str]:
    """Calculate the measurement value from the source measurements."""
    if not sources:
        return None
    values = []
    for source in sources:
        if source["parse_error"] or source["connection_error"]:
            return None
        entities_to_ignore = [
            entity for entity in source.get("entity_user_data", {}).values()
            if entity.get("status") in ("fixed", "false_positive", "wont_fix")]
        values.append(int(source["value"]) - len(entities_to_ignore))
    add = dict(max=max, min=min, sum=sum)[addition]
    return str(add(values))  # type: ignore


def determine_measurement_status(datamodel, metric, measurement_value: Optional[str]) -> Optional[str]:
    """Determine the measurement status."""
    if measurement_value is None:
        return None
    direction = datamodel["metrics"][metric["type"]]["direction"]
    value = int(measurement_value)
    target = int(metric["target"])
    near_target = int(metric["near_target"])
    debt_target = int(metric["debt_target"] or target)
    debt_end_date = metric.get("debt_end_date", date.max.isoformat())
    better_or_equal = {"≧": int.__ge__, "≦": int.__le__, "=": int.__eq__}[direction]
    if better_or_equal(value, target):
        status = "target_met"
    elif metric["accept_debt"] and date.today().isoformat() <= debt_end_date and better_or_equal(value, debt_target):
        status = "debt_target_met"
    elif better_or_equal(target, near_target) and better_or_equal(value, near_target):
        status = "near_target_met"
    else:
        status = "target_not_met"
    return status
