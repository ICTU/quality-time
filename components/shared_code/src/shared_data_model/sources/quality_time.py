"""Quality-time source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import (
    Color,
    Entity,
    EntityAttribute,
    EntityAttributeAlignment,
    EntityAttributeType,
)
from shared_data_model.meta.source import Source
from shared_data_model.meta.unit import Unit
from shared_data_model.parameters import (
    URL,
    IntegerParameter,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
)

ALL_QUALITY_TIME_METRICS = ["metrics", "missing_metrics", "source_up_to_dateness", "source_version"]

QUALITY_TIME = Source(
    name="Quality-time",
    description="Quality report software for software development and maintenance.",
    url=HttpUrl("https://github.com/ICTU/quality-time"),
    parameters={
        "url": URL(
            name="Quality-time URL",
            help="URL of the Quality-time instance, with port if necessary, but without path. For example, "
            "'https://quality-time.example.org'.",
            validate_on=[],
            metrics=ALL_QUALITY_TIME_METRICS,
        ),
        "status": MultipleChoiceParameter(
            name="Metric statuses",
            placeholder="all statuses",
            values=[
                "informative (blue)",
                "target met (green)",
                "near target met (yellow)",
                "target not met (red)",
                "technical debt target met (grey)",
                "unknown (white)",
            ],
            api_values={
                "informative (blue)": "informative",
                "target met (green)": "target_met",
                "near target met (yellow)": "near_target_met",
                "target not met (red)": "target_not_met",
                "technical debt target met (grey)": "debt_target_met",
                "unknown (white)": "unknown",
            },
            metrics=["metrics"],
        ),
        "min_status_duration": IntegerParameter(
            name="Minimum metric status duration",
            short_name="minimum status duration",
            help="Only count metrics whose status has not changed for the given number of days.",
            unit=Unit.DAYS,
            min_value="0",
            default_value="0",
            metrics=["metrics"],
        ),
        "reports": MultipleChoiceWithAdditionParameter(
            name="Report names or identifiers",
            short_name="reports",
            placeholder="all reports",
            metrics=["metrics", "source_up_to_dateness", "missing_metrics"],
        ),
        "metric_type": MultipleChoiceParameter(
            name="Metric types",
            help="If provided, only count metrics with the selected metric types.",
            placeholder="all metric types",
            values=[
                "Average issue lead time",
                "Change failure rate",
                "CI-pipeline duration",
                "Commented out code",
                "Complex units",
                "Dependencies",
                "Duplicated lines",
                "Failed CI-jobs",
                "Inactive branches",
                "Issues",
                "Job runs within time period",
                "Violation remediation effort",
                "Long units",
                "Manual test duration",
                "Manual test execution",
                "Many parameters",
                "Merge requests",
                "Metrics",
                "Missing metrics",
                "Performancetest duration",
                "Performancetest stability",
                "Scalability",
                "Security warnings",
                "Size (LOC)",
                "Slow transactions",
                "Software version",
                "Source up-to-dateness",
                "Source version",
                "Suppressed violations",
                "Test branch coverage",
                "Test line coverage",
                "Test cases",
                "Test suites",
                "Tests",
                "Time remaining",
                "Todo and fixme comments",
                "Unused CI-jobs",
                "User story points",
                "Velocity",
                "Violations",
                "Sentiment",
            ],
            api_values={
                "Average issue lead time": "average_issue_lead_time",
                "Change failure rate": "change_failure_rate",
                "CI-pipeline duration": "pipeline_duration",
                "Commented out code": "commented_out_code",
                "Complex units": "complex_units",
                "Dependencies": "dependencies",
                "Duplicated lines": "duplicated_lines",
                "Failed CI-jobs": "failed_jobs",
                "Inactive branches": "inactive_branches",
                "Issues": "issues",
                "Job runs within time period": "job_runs_within_time_period",
                "Long units": "long_units",
                "Manual test duration": "manual_test_duration",
                "Manual test execution": "manual_test_execution",
                "Many parameters": "many_parameters",
                "Merge requests": "merge_requests",
                "Metrics": "metrics",
                "Missing metrics": "missing_metrics",
                "Performancetest duration": "performancetest_duration",
                "Performancetest stability": "performancetest_stability",
                "Scalability": "scalability",
                "Security warnings": "security_warnings",
                "Size (LOC)": "loc",
                "Slow transactions": "slow_transactions",
                "Software version": "software_version",
                "Source up-to-dateness": "source_up_to_dateness",
                "Source version": "source_version",
                "Suppressed violations": "suppressed_violations",
                "Test branch coverage": "uncovered_branches",
                "Test line coverage": "uncovered_lines",
                "Test cases": "test_cases",
                "Test suites": "test_suites",
                "Tests": "tests",
                "Time remaining": "time_remaining",
                "Todo and fixme comments": "todo_and_fixme_comments",
                "Unused CI-jobs": "unused_jobs",
                "User story points": "user_story_points",
                "Velocity": "velocity",
                "Violations": "violations",
                "Violation remediation effort": "remediation_effort",
                "Sentiment": "sentiment",
            },
            metrics=["metrics"],
        ),
        "source_type": MultipleChoiceParameter(
            name="Source types",
            help="If provided, only count metrics with one or more sources of the selected source types.",
            placeholder="all source types",
            values=[
                "Anchore",
                "Anchore Jenkins plugin",
                "Axe CSV",
                "Axe HTML reporter",
                "Axe-core",
                "Azure DevOps Server",
                "Bandit",
                "Bitbucket",
                "Calendar date",
                "Cargo Audit",
                "Checkmarx CxSAST",
                "cloc",
                "Cobertura",
                "Cobertura Jenkins plugin",
                "Composer",
                "Dependency-Track",
                "Gatling",
                "GitHub",
                "GitLab",
                "Harbor",
                "Harbor JSON",
                "JaCoCo",
                "JaCoCo Jenkins plugin",
                "Jenkins",
                "Jenkins test report",
                "Jira",
                "JMeter CSV",
                "JMeter JSON",
                "JSON file with security warnings",
                "JUnit XML report",
                "Manual number",
                "NCover",
                "npm",
                "OJAudit",
                "OpenVAS",
                "OWASP Dependency-Check",
                "OWASP ZAP",
                "Performancetest-runner",
                "pip",
                "Pyupio Safety",
                "Quality-time",
                "Robot Framework",
                "Robot Framework Jenkins plugin",
                "SARIF",
                "Snyk",
                "SonarQube",
                "TestNG",
                "Trello",
                "Trivy JSON",
                "Visual Studio TRX",
            ],
            api_values={
                "Anchore": "anchore",
                "Anchore Jenkins plugin": "anchore_jenkins_plugin",
                "Axe CSV": "axecsv",
                "Axe HTML reporter": "axe_html_reporter",
                "Axe-core": "axe_core",
                "Azure DevOps Server": "azure_devops",
                "Bandit": "bandit",
                "Bitbucket": "bitbucket",
                "Calendar date": "calendar",
                "Cargo Audit": "cargo_audit",
                "Checkmarx CxSAST": "cxsast",
                "cloc": "cloc",
                "Cobertura": "cobertura",
                "Cobertura Jenkins plugin": "cobertura_jenkins_plugin",
                "Composer": "composer",
                "Dependency-Track": "dependency_track",
                "Gatling": "gatling",
                "GitHub": "github",
                "GitLab": "gitlab",
                "Harbor": "harbor",
                "Harbor JSON": "harbor_json",
                "JaCoCo": "jacoco",
                "JaCoCo Jenkins plugin": "jacoco_jenkins_plugin",
                "Jenkins": "jenkins",
                "Jenkins test report": "jenkins_test_report",
                "Jira": "jira",
                "JMeter CSV": "jmeter_csv",
                "JMeter JSON": "jmeter_json",
                "JSON file with security warnings": "generic_json",
                "JUnit XML report": "junit",
                "Manual number": "manual_number",
                "NCover": "ncover",
                "npm": "npm",
                "OJAudit": "ojaudit",
                "OpenVAS": "openvas",
                "OWASP Dependency-Check": "owasp_dependency_check",
                "OWASP ZAP": "owasp_zap",
                "Performancetest-runner": "performancetest_runner",
                "pip": "pip",
                "Pyupio Safety": "pyupio_safety",
                "Quality-time": "quality_time",
                "Robot Framework": "robot_framework",
                "Robot Framework Jenkins plugin": "robot_framework_jenkins_plugin",
                "SARIF": "sarif_json",
                "Snyk": "snyk",
                "SonarQube": "sonarqube",
                "TestNG": "testng",
                "Trello": "trello",
                "Trivy JSON": "trivy_json",
                "Visual Studio TRX": "visual_studio_trx",
            },
            metrics=["metrics"],
        ),
        "subjects_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Subjects to ignore (subject names or identifiers)",
            short_name="subjects to ignore",
            help="The Quality-time missing metrics collector will ignore metrics that are missing in the "
            "list of subjects to ignore.",
            metrics=["missing_metrics"],
        ),
        "tags": MultipleChoiceWithAdditionParameter(
            name="Tags",
            help="If provided, only count metrics with one ore more of the given tags.",
            placeholder="all tags",
            metrics=["metrics"],
        ),
    },
    entities={
        "metrics": Entity(
            name="metric",
            attributes=[
                EntityAttribute(name="Report", url="report_url"),
                EntityAttribute(name="Subject", url="subject_url"),
                EntityAttribute(name="Metric", url="metric_url"),
                EntityAttribute(
                    name="Status",
                    type=EntityAttributeType.STATUS,
                    color={
                        "target_met": Color.POSITIVE,
                        "near_target_met": Color.WARNING,
                        "target_not_met": Color.NEGATIVE,
                        "technical_debt_target_met": Color.ACTIVE,
                    },
                ),
                EntityAttribute(name="Status start date", type=EntityAttributeType.DATE),
                EntityAttribute(name="Measurement", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Target", alignment=EntityAttributeAlignment.RIGHT),
                EntityAttribute(name="Unit"),
            ],
        ),
        "missing_metrics": Entity(
            name="metric type",
            attributes=[
                EntityAttribute(name="Report", url="report_url"),
                EntityAttribute(name="Subject", url="subject_url"),
                EntityAttribute(name="Subject type", url="subject_type_url"),
                EntityAttribute(name="Metric type", url="metric_type_url"),
            ],
        ),
    },
)
