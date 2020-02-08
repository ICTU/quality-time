"""Anchore metrics collector."""

from .source_collector import FileSourceCollector, SourceUpToDatenessCollector


class AnchoreSecurityWarnings(FileSourceCollector):
    """Anchore collector for security warnings."""
