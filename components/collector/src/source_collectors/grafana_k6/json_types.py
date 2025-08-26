"""Grafana k6 JSON types."""

from typing import Literal, NotRequired

from typing_extensions import TypedDict


class ThresholdEvaluation(TypedDict):
    """Class representing a Grafana k6 threshold evaluation."""

    ok: bool


class Values(TypedDict, extra_items=float):  # type: ignore[call-arg]
    """Class representing the values of a Grafana k6 metric, if metric.contains == "time"."""

    # Note that in addition to the values below, the metric values may also include other values such as p95, p99, etc.
    # Since these can be defined by the user of Grafana k6 we can't list them exhaustively, but need to allow for
    # extra items. Unfortunately, typing.TypedDict does not support extra items yet, so we use
    # typing_extensions.TypedDict instead. mypy does not support extra items yet either, so we also need to
    # suppress the mypy errors.

    count: int
    avg: float
    min: float
    med: float
    max: float


class Metric(TypedDict):
    """Class representing a Grafana k6 metric.

    See https://grafana.com/docs/k6/latest/results-output/end-of-test/custom-summary/#metric-schema.
    """

    contains: Literal["data", "default", "time"]
    thresholds: NotRequired[dict[str, ThresholdEvaluation]]
    values: Values


class State(TypedDict):
    """Class representing the state object in a summary.json file."""

    testRunDurationMs: float


class SummaryJSON(TypedDict):
    """Class representing a Grafana k6 summary.json file.

    See https://grafana.com/docs/k6/latest/results-output/end-of-test/custom-summary/#summary-data-reference.
    """

    metrics: dict[str, Metric]
    state: State
