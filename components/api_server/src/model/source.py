"""Source context."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.report import Report
    from shared.model.metric import Metric
    from shared.model.source import Source
    from shared.model.subject import Subject


@dataclass
class SourceContext:
    """Source, combined with its containing metric, subject, and report."""

    metric: Metric
    report: Report
    source: Source
    subject: Subject
