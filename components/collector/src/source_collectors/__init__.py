"""Metric collectors per source."""

from .anchore import AnchoreSecurityWarnings, AnchoreSourceUpToDateness
from .axe_csv import AxeCSVAccessibility
from .azure_devops import AzureDevopsIssues, AzureDevopsReadyUserStoryPoints
from .bandit import BanditSecurityWarnings, BanditSourceUpToDateness
from .calendar import CalendarSourceUpToDateness
from .cxsast import CxSASTSecurityWarnings, CxSASTSourceUpToDateness
from .gitlab import GitLabFailedJobs, GitLabUnusedJobs, GitLabSourceUpToDateness, GitLabUnmergedBranches
from .jacoco import JacocoSourceUpToDateness, JacocoUncoveredBranches, JacocoUncoveredLines
from .jacoco_jenkins_plugin import (
    JacocoJenkinsPluginUncoveredBranches, JacocoJenkinsPluginUncoveredLines, JacocoJenkinsPluginSourceUpToDateness)
from .jenkins import JenkinsFailedJobs, JenkinsJobs
from .jenkins_test_report import JenkinsTestReportSourceUpToDateness, JenkinsTestReportTests
from .jira import JiraIssues, JiraManualTestDuration, JiraManualTestExecution, JiraReadyUserStoryPoints
from .junit import JUnitSourceUpToDateness, JUnitTests
from .manual_number import ManualNumber
from .ncover import NCoverSourceUpToDateness
from .ojaudit import OJAuditViolations
from .openvas import OpenVASSecurityWarnings, OpenVASSourceUpToDateness
from .owasp_dependency_check import OWASPDependencyCheckSecurityWarnings, OWASPDependencyCheckSourceUpToDateness
from .owasp_dependency_check_jenkins_plugin import (
    OWASPDependencyCheckJenkinsPluginSecurityWarnings, OWASPDependencyCheckJenkinsPluginSourceUpToDateness)
from .owasp_zap import OWASPZAPSecurityWarnings, OWASPZAPSourceUpToDateness
from .performancetest_runner import (
    PerformanceTestRunnerPerformanceTestDuration, PerformanceTestRunnerPerformanceTestStability,
    PerformanceTestRunnerScalability, PerformanceTestRunnerSlowTransactions, PerformanceTestRunnerSourceUpToDateness,
    PerformanceTestRunnerTests)
from .pyupio_safety import PyupioSafetySecurityWarnings
from .quality_time import QualityTimeMetrics
from .random_number import Random
from .robot_framework import RobotFrameworkTests, RobotFrameworkSourceUpToDateness
from .sonarqube import (
    SonarQubeDuplicatedLines, SonarQubeComplexUnits, SonarQubeCommentedOutCode, SonarQubeLOC,
    SonarQubeLongUnits, SonarQubeManyParameters, SonarQubeSourceUpToDateness, SonarQubeSuppressedViolations,
    SonarQubeTests, SonarQubeUncoveredBranches, SonarQubeUncoveredLines, SonarQubeViolations)
from .trello import TrelloIssues, TrelloSourceUpToDateness
from .wekan import WekanIssues, WekanSourceUpToDateness
