"""Anchore Jenkins plugin time passed collector."""

from base_collectors import JenkinsPluginTimePassedCollector


class AnchoreJenkinsPluginTimePassed(JenkinsPluginTimePassedCollector):
    """Collector for the time passed since the lastest Anchore Jenkins plugin security report."""
