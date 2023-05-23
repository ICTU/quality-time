"""Model iterators."""

from collections.abc import Iterator

from shared.model.report import Report


def subjects(*reports: Report) -> Iterator:
    """Return all subjects in the reports."""
    for report in reports:
        yield from report.get("subjects", {}).values()


def metrics(*reports: Report) -> Iterator:
    """Return all metrics in the reports."""
    for subject in subjects(*reports):
        yield from subject.get("metrics", {}).values()


def sources(*reports: Report) -> Iterator:
    """Return all sources in the reports."""
    for metric in metrics(*reports):
        yield from metric.get("sources", {}).values()
