"""Metric collectors per source."""

from .axe_csv import AxeCSVAccessibility
from .azure_devops import AzureDevopsIssues, AzureDevopsReadyUserStoryPoints
from .bandit import BanditSecurityWarnings, BanditSourceUpToDateness
from .calendar import CalendarSourceUpToDateness
from .cxsast import CxSASTSecurityWarnings, CxSASTSourceUpToDateness
from .gitlab import GitlabFailedJobs, GitlabSourceUpToDateness, GitlabUnmergedBranches
from .hq import HQ
from .jacoco import JacocoSourceUpToDateness, JacocoUncoveredBranches, JacocoUncoveredLines
from .jenkins import JenkinsFailedJobs, JenkinsJobs
from .jenkins_test_report import (
    JenkinsTestReportSourceUpToDateness, JenkinsTestReportFailedTests, JenkinsTestReportTests)
from .jira import JiraIssues, JiraManualTestDuration, JiraReadyUserStoryPoints
from .junit import JUnitFailedTests, JUnitSourceUpToDateness, JUnitTests
from .manual_number import ManualNumber
from .ncover import NCoverSourceUpToDateness
from .ojaudit import OJAuditViolations
from .openvas import OpenVASSecurityWarnings, OpenVASSourceUpToDateness
from .owasp_dependency_check import OWASPDependencyCheckSecurityWarnings, OWASPDependencyCheckSourceUpToDateness
from .owasp_dependency_check_jenkins_plugin import (
    OWASPDependencyCheckJenkinsPluginSecurityWarnings, OWASPDependencyCheckJenkinsPluginSourceUpToDateness)
from .owasp_zap import OWASPZAPSecurityWarnings, OWASPZAPSourceUpToDateness
from .performancetest_runner import (
    PerformanceTestRunnerFailedTests, PerformanceTestRunnerPerformanceTestDuration,
    PerformanceTestRunnerPerformanceTestStability, PerformanceTestRunnerScalability,
    PerformanceTestRunnerSlowTransactions, PerformanceTestRunnerSourceUpToDateness, PerformanceTestRunnerTests)
from .pyupio_safety import PyupioSafetySecurityWarnings
from .quality_time import QualityTimeMetrics
from .random_number import Random
from .robot_framework import RobotFrameworkTests, RobotFrameworkSourceUpToDateness, RobotFrameworkFailedTests
from .sonarqube import (
    SonarQubeDuplicatedLines, SonarQubeComplexUnits, SonarQubeCommentedOutCode, SonarQubeFailedTests, SonarQubeLOC,
    SonarQubeLongUnits, SonarQubeManyParameters, SonarQubeNCLOC, SonarQubeSourceUpToDateness,
    SonarQubeSuppressedViolations, SonarQubeTests, SonarQubeUncoveredBranches, SonarQubeUncoveredLines,
    SonarQubeViolations)
from .trello import TrelloIssues, TrelloSourceUpToDateness
from .wekan import WekanIssues, WekanSourceUpToDateness
