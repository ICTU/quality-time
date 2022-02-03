"""Source collectors."""

from .anchore.security_warnings import AnchoreSecurityWarnings
from .anchore.time_passed import AnchoreTimePassed

from .anchore_jenkins_plugin.security_warnings import AnchoreJenkinsPluginSecurityWarnings
from .anchore_jenkins_plugin.time_passed import AnchoreJenkinsPluginTimePassed

from .axe_core.accessibility import AxeCoreAccessibility
from .axe_core.time_passed import AxeCoreTimePassed
from .axe_core.source_version import AxeCoreSourceVersion

from .axe_csv.accessibility import AxeCSVAccessibility

from .axe_html_reporter.accessibility import AxeHTMLReporterAccessibility

from .azure_devops.failed_jobs import AzureDevopsFailedJobs
from .azure_devops.issues import AzureDevopsIssues
from .azure_devops.merge_requests import AzureDevopsMergeRequests
from .azure_devops.time_passed import AzureDevopsTimePassed
from .azure_devops.tests import AzureDevopsTests
from .azure_devops.unmerged_branches import AzureDevopsUnmergedBranches
from .azure_devops.unused_jobs import AzureDevopsUnusedJobs
from .azure_devops.user_story_points import AzureDevopsUserStoryPoints

from .bandit.security_warnings import BanditSecurityWarnings
from .bandit.time_passed import BanditTimePassed

from .calendar.time_passed import CalendarTimePassed

from .cloc.loc import ClocLOC
from .cloc.source_version import ClocSourceVersion

from .cobertura.time_passed import CoberturaTimePassed
from .cobertura.source_version import CoberturaSourceVersion
from .cobertura.uncovered_branches import CoberturaUncoveredBranches
from .cobertura.uncovered_lines import CoberturaUncoveredLines

from .cobertura_jenkins_plugin.time_passed import CoberturaJenkinsPluginTimePassed
from .cobertura_jenkins_plugin.uncovered_branches import CoberturaJenkinsPluginUncoveredBranches
from .cobertura_jenkins_plugin.uncovered_lines import CoberturaJenkinsPluginUncoveredLines

from .composer.dependencies import ComposerDependencies

from .cxsast.security_warnings import CxSASTSecurityWarnings
from .cxsast.time_passed import CxSASTTimePassed
from .cxsast.source_version import CxSASTSourceVersion

from .gatling.performancetest_duration import GatlingPerformanceTestDuration
from .gatling.slow_transactions import GatlingSlowTransactions
from .gatling.time_passed import GatlingTimePassed
from .gatling.source_version import GatlingLogCollector
from .gatling.tests import GatlingTests

from .generic_json.security_warnings import GenericJSONSecurityWarnings

from .gitlab.failed_jobs import GitLabFailedJobs
from .gitlab.merge_requests import GitLabMergeRequests
from .gitlab.time_passed import GitLabTimePassed
from .gitlab.source_version import GitLabSourceVersion
from .gitlab.unmerged_branches import GitLabUnmergedBranches
from .gitlab.unused_jobs import GitLabUnusedJobs

from .jacoco.time_passed import JacocoTimePassed
from .jacoco.uncovered_branches import JacocoUncoveredBranches
from .jacoco.uncovered_lines import JacocoUncoveredLines

from .jacoco_jenkins_plugin.time_passed import JacocoJenkinsPluginTimePassed
from .jacoco_jenkins_plugin.uncovered_branches import JacocoJenkinsPluginUncoveredBranches
from .jacoco_jenkins_plugin.uncovered_lines import JacocoJenkinsPluginUncoveredLines

from .jenkins.failed_jobs import JenkinsFailedJobs
from .jenkins.time_passed import JenkinsTimePassed
from .jenkins.source_version import JenkinsSourceVersion
from .jenkins.unused_jobs import JenkinsUnusedJobs

from .jenkins_test_report.time_passed import JenkinsTestReportTimePassed
from .jenkins_test_report.test_cases import JenkinsTestReportTestCases
from .jenkins_test_report.tests import JenkinsTestReportTests

from .jira.issue_status import JiraIssueStatus
from .jira.issues import JiraIssues
from .jira.manual_test_duration import JiraManualTestDuration
from .jira.manual_test_execution import JiraManualTestExecution
from .jira.source_version import JiraSourceVersion
from .jira.test_cases import JiraTestCases
from .jira.user_story_points import JiraUserStoryPoints
from .jira.velocity import JiraVelocity

from .jmeter_csv.performancetest_duration import JMeterCSVPerformanceTestDuration
from .jmeter_csv.slow_transactions import JMeterCSVSlowTransactions
from .jmeter_csv.time_passed import JMeterCSVTimePassed
from .jmeter_csv.tests import JMeterCSVTests

from .jmeter_json.slow_transactions import JMeterJSONSlowTransactions
from .jmeter_json.tests import JMeterJSONTests

from .junit.time_passed import JUnitTimePassed
from .junit.test_cases import JUnitTestCases
from .junit.tests import JUnitTests

from .manual_number.all_metrics import ManualNumber

from .ncover.uncovered_branches import NCoverUncoveredBranches
from .ncover.uncovered_lines import NCoverUncoveredLines
from .ncover.time_passed import NCoverTimePassed

from .npm.dependencies import NpmDependencies

from .ojaudit.violations import OJAuditViolations

from .openvas.security_warnings import OpenVASSecurityWarnings
from .openvas.time_passed import OpenVASTimePassed
from .openvas.source_version import OpenVASSourceVersion

from .owasp_dependency_check.dependencies import OWASPDependencyCheckDependencies
from .owasp_dependency_check.security_warnings import OWASPDependencyCheckSecurityWarnings
from .owasp_dependency_check.time_passed import OWASPDependencyCheckTimePassed
from .owasp_dependency_check.source_version import OWASPDependencyCheckSourceVersion

from .owasp_zap.security_warnings import OWASPZAPSecurityWarnings
from .owasp_zap.time_passed import OWASPZAPTimePassed
from .owasp_zap.source_version import OWASPZAPSourceVersion

from .performancetest_runner.performancetest_duration import PerformanceTestRunnerPerformanceTestDuration
from .performancetest_runner.performancetest_scalability import PerformanceTestRunnerScalability
from .performancetest_runner.performancetest_stability import PerformanceTestRunnerPerformanceTestStability
from .performancetest_runner.slow_transactions import PerformanceTestRunnerSlowTransactions
from .performancetest_runner.time_passed import PerformanceTestRunnerTimePassed
from .performancetest_runner.tests import PerformanceTestRunnerTests

from .pip.dependencies import PipDependencies

from .pyupio_safety.security_warnings import PyupioSafetySecurityWarnings

from .quality_time.metrics import QualityTimeMetrics
from .quality_time.missing_metrics import QualityTimeMissingMetrics
from .quality_time.time_passed import QualityTimeTimePassed
from .quality_time.source_version import QualityTimeSourceVersion

from .robot_framework.time_passed import RobotFrameworkTimePassed
from .robot_framework.source_version import RobotFrameworkSourceVersion
from .robot_framework.test_cases import RobotFrameworkTestCases
from .robot_framework.tests import RobotFrameworkTests

from .robot_framework_jenkins_plugin.time_passed import RobotFrameworkJenkinsPluginTimePassed
from .robot_framework_jenkins_plugin.tests import RobotFrameworkJenkinsPluginTests

from .snyk.security_warnings import SnykSecurityWarnings

from .sonarqube.commented_out_code import SonarQubeCommentedOutCode
from .sonarqube.complex_units import SonarQubeComplexUnits
from .sonarqube.duplicated_lines import SonarQubeDuplicatedLines
from .sonarqube.loc import SonarQubeLOC
from .sonarqube.long_units import SonarQubeLongUnits
from .sonarqube.many_parameters import SonarQubeManyParameters
from .sonarqube.remediation_effort import SonarQubeRemediationEffort
from .sonarqube.security_warnings import SonarQubeSecurityWarnings
from .sonarqube.time_passed import SonarQubeTimePassed
from .sonarqube.source_version import SonarQubeSourceVersion
from .sonarqube.suppressed_violations import SonarQubeSuppressedViolations
from .sonarqube.tests import SonarQubeTests
from .sonarqube.uncovered_branches import SonarQubeUncoveredBranches
from .sonarqube.uncovered_lines import SonarQubeUncoveredLines
from .sonarqube.violations import SonarQubeViolations

from .testng.time_passed import TestNGTimePassed
from .testng.test_cases import TestNGTestCases
from .testng.tests import TestNGTests

from .trello.issues import TrelloIssues
from .trello.time_passed import TrelloTimePassed
