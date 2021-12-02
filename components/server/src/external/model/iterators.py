"""Model iterators."""

from collections.abc import Iterator


def subjects(*reports) -> Iterator:
    """Return all subjects in the reports."""
    for report in reports:
        yield from report.get("subjects", {}).values()


def metrics(*reports) -> Iterator:
    """Return all metrics in the reports."""
    for subject in subjects(*reports):
        yield from subject.get("metrics", {}).values()


def sources(*reports) -> Iterator:
    """Return all sources in the reports."""
    for metric in metrics(*reports):
        yield from metric.get("sources", {}).values()
