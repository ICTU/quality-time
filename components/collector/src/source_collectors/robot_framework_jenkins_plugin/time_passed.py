"""Robot Framework Jenkins plugin time passed collector."""

from base_collectors import JenkinsPluginTimePassedCollector

from .base import RobotFrameworkJenkinsPluginBaseClass


class RobotFrameworkJenkinsPluginTimePassed(RobotFrameworkJenkinsPluginBaseClass, JenkinsPluginTimePassedCollector):
    """Collector for the time passed tince the latest Robot Framework Jenkins plugin coverage report."""
