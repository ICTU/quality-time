"""Model iterators."""

from collections.abc import Iterator


def sources(reports) -> Iterator:
    """Return all sources in the reports."""
    for report in reports:
        for subject in report.get("subjects", {}).values():
            for metric in subject.get("metrics", {}).values():
                yield from metric.get("sources", {}).values()
