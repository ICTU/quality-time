"""Metric collectors per source."""

from .api_source_collectors.azure_devops.issues import AzureDevopsIssues
from .api_source_collectors.azure_devops.jobs import AzureDevopsFailedJobs, AzureDevopsUnusedJobs
from .api_source_collectors.azure_devops.merge_requests import AzureDevopsMergeRequests
from .api_source_collectors.azure_devops.tests import AzureDevopsTests
from .api_source_collectors.azure_devops.unmerged_branches import AzureDevopsUnmergedBranches
from .api_source_collectors.azure_devops.source_up_to_dateness import AzureDevopsSourceUpToDateness
from .api_source_collectors.azure_devops.user_story_points import AzureDevopsUserStoryPoints
from .api_source_collectors.cobertura_jenkins_plugin.source_up_to_dateness import (
    CoberturaJenkinsPluginSourceUpToDateness,
)
from .api_source_collectors.cobertura_jenkins_plugin.uncovered_branches import CoberturaJenkinsPluginUncoveredBranches
from .api_source_collectors.cobertura_jenkins_plugin.uncovered_lines import CoberturaJenkinsPluginUncoveredLines
from .api_source_collectors.cxsast.security_warnings import CxSASTSecurityWarnings
from .api_source_collectors.cxsast.source_up_to_dateness import CxSASTSourceUpToDateness
from .api_source_collectors.gitlab.jobs import GitLabFailedJobs, GitLabUnusedJobs
from .api_source_collectors.gitlab.merge_requests import GitLabMergeRequests
from .api_source_collectors.gitlab.source_up_to_dateness import GitLabSourceUpToDateness
from .api_source_collectors.gitlab.unmerged_branches import GitLabUnmergedBranches
from .api_source_collectors.jacoco_jenkins_plugin.source_up_to_dateness import JacocoJenkinsPluginSourceUpToDateness
from .api_source_collectors.jacoco_jenkins_plugin.uncovered_branches import JacocoJenkinsPluginUncoveredBranches
from .api_source_collectors.jacoco_jenkins_plugin.uncovered_lines import JacocoJenkinsPluginUncoveredLines
from .api_source_collectors.jenkins.failed_jobs import JenkinsFailedJobs
from .api_source_collectors.jenkins.source_up_to_dateness import JenkinsSourceUpToDateness
from .api_source_collectors.jenkins.unused_jobs import JenkinsUnusedJobs
from .api_source_collectors.jenkins_test_report.source_up_to_dateness import JenkinsTestReportSourceUpToDateness
from .api_source_collectors.jenkins_test_report.tests import JenkinsTestReportTests
from .api_source_collectors.jira.issues import JiraIssues
from .api_source_collectors.jira.manual_test_duration import JiraManualTestDuration
from .api_source_collectors.jira.manual_test_execution import JiraManualTestExecution
from .api_source_collectors.jira.user_story_points import JiraUserStoryPoints
from .api_source_collectors.jira.velocity import JiraVelocity
from .api_source_collectors.quality_time.metrics import QualityTimeMetrics
from .api_source_collectors.quality_time.source_up_to_dateness import QualityTimeSourceUpToDateness
from .api_source_collectors.robot_framework_jenkins_plugin.source_up_to_dateness import (
    RobotFrameworkJenkinsPluginSourceUpToDateness,
)
from .api_source_collectors.robot_framework_jenkins_plugin.tests import RobotFrameworkJenkinsPluginTests
from .api_source_collectors.sonarqube.commented_out_code import SonarQubeCommentedOutCode
from .api_source_collectors.sonarqube.complex_units import SonarQubeComplexUnits
from .api_source_collectors.sonarqube.duplicated_lines import SonarQubeDuplicatedLines
from .api_source_collectors.sonarqube.loc import SonarQubeLOC
from .api_source_collectors.sonarqube.long_units import SonarQubeLongUnits
from .api_source_collectors.sonarqube.many_parameters import SonarQubeManyParameters
from .api_source_collectors.sonarqube.remediation_effort import SonarQubeRemediationEffort
from .api_source_collectors.sonarqube.security_warnings import SonarQubeSecurityWarnings
from .api_source_collectors.sonarqube.source_up_to_dateness import SonarQubeSourceUpToDateness
from .api_source_collectors.sonarqube.suppressed_violations import SonarQubeSuppressedViolations
from .api_source_collectors.sonarqube.tests import SonarQubeTests
from .api_source_collectors.sonarqube.uncovered_branches import SonarQubeUncoveredBranches
from .api_source_collectors.sonarqube.uncovered_lines import SonarQubeUncoveredLines
from .api_source_collectors.sonarqube.violations import SonarQubeViolations
from .api_source_collectors.trello.issues import TrelloIssues
from .api_source_collectors.trello.source_up_to_dateness import TrelloSourceUpToDateness
from .api_source_collectors.wekan.issues import WekanIssues
from .api_source_collectors.wekan.source_up_to_dateness import WekanSourceUpToDateness
from .file_source_collectors.anchore.security_warnings import AnchoreSecurityWarnings
from .file_source_collectors.anchore.source_up_to_dateness import AnchoreSourceUpToDateness
from .file_source_collectors.axe_csv.accessibility import AxeCSVAccessibility
from .file_source_collectors.axe_selenium_python.accessibility import AxeSeleniumPythonAccessibility
from .file_source_collectors.axe_selenium_python.source_up_to_dateness import AxeSeleniumPythonSourceUpToDateness
from .file_source_collectors.bandit import BanditSecurityWarnings, BanditSourceUpToDateness
from .file_source_collectors.cloc import ClocLOC
from .file_source_collectors.cobertura import (
    CoberturaSourceUpToDateness,
    CoberturaUncoveredBranches,
    CoberturaUncoveredLines,
)
from .file_source_collectors.composer import ComposerDependencies
from .file_source_collectors.generic_json import GenericJSONSecurityWarnings
from .file_source_collectors.jacoco import JacocoSourceUpToDateness, JacocoUncoveredBranches, JacocoUncoveredLines
from .file_source_collectors.junit import JUnitSourceUpToDateness, JUnitTests
from .file_source_collectors.ncover import NCoverSourceUpToDateness
from .file_source_collectors.npm import NpmDependencies
from .file_source_collectors.ojaudit import OJAuditViolations
from .file_source_collectors.openvas import OpenVASSecurityWarnings, OpenVASSourceUpToDateness
from .file_source_collectors.owasp_dependency_check import (
    OWASPDependencyCheckDependencies,
    OWASPDependencyCheckSecurityWarnings,
    OWASPDependencyCheckSourceUpToDateness,
)
from .file_source_collectors.owasp_zap import OWASPZAPSecurityWarnings, OWASPZAPSourceUpToDateness
from .file_source_collectors.performancetest_runner import (
    PerformanceTestRunnerPerformanceTestDuration,
    PerformanceTestRunnerPerformanceTestStability,
    PerformanceTestRunnerScalability,
    PerformanceTestRunnerSlowTransactions,
    PerformanceTestRunnerSourceUpToDateness,
    PerformanceTestRunnerTests,
)
from .file_source_collectors.pip import PipDependencies
from .file_source_collectors.pyupio_safety import PyupioSafetySecurityWarnings
from .file_source_collectors.robot_framework import RobotFrameworkSourceUpToDateness, RobotFrameworkTests
from .file_source_collectors.snyk import SnykSecurityWarnings
from .file_source_collectors.testng import TestNGSourceUpToDateness, TestNGTests
from .local_source_collectors.calendar import CalendarSourceUpToDateness
from .local_source_collectors.manual_number import ManualNumber
from .local_source_collectors.random_number import Random
