"""Model iterators."""

from typing import Iterator


def sources(report) -> Iterator:
    """Return all sources in the report."""
    for subject in report.get("subjects", {}).values():
        for metric in subject.get("metrics", {}).values():
            yield from metric.get("sources", {}).items()
