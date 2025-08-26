"""Unit tests for database migrations."""

from collections.abc import Mapping

from initialization.migrations import perform_migrations

from tests.base import DataModelTestCase, disable_logging
from tests.fixtures import SourceId, REPORT_ID, SUBJECT_ID, METRIC_ID, METRIC_ID2, METRIC_ID3, SOURCE_ID, SOURCE_ID2


class MigrationTestCase(DataModelTestCase):
    """Base class for migration unit tests."""

    def existing_report(
        self,
        *,
        metric_type: str,
        metric_name: str = "",
        metric_unit: str = "",
        sources: Mapping[SourceId, Mapping[str, str | Mapping[str, str]]] | None = None,
    ):
        """Return a report fixture. To be extended in subclasses."""
        report: dict = {
            "_id": "id",
            "report_uuid": REPORT_ID,
            "subjects": {SUBJECT_ID: {"type": "software", "metrics": {METRIC_ID: {"type": metric_type}}}},
        }
        if metric_name:
            report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["name"] = metric_name
        if metric_unit:
            report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["unit"] = metric_unit
        if sources is not None:
            report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"] = sources
        return report

    def inserted_report(self, **kwargs):
        """Return a report as it is expected to have been inserted into the reports collection.

        By default, this is the name as the existing report, except for the _id being removed.
        """
        report = self.existing_report(**kwargs)
        del report["_id"]
        return report

    def check_inserted_report(self, inserted_report):
        """Check that the report was inserted."""
        self.database.reports.replace_one.assert_called_once_with({"_id": "id"}, inserted_report)


class NoOpMigrationTest(MigrationTestCase):
    """Unit tests for empty database and empty reports."""

    def test_no_reports(self):
        """Test that the migration succeeds without reports."""
        self.database.reports.find.return_value = []
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_empty_reports(self):
        """Test that the migration succeeds when the report does not have anything to migrate."""
        self.database.reports.find.return_value = [self.existing_report(metric_type="issues")]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()


class ChangeAccessibilityViolationsTest(MigrationTestCase):
    """Unit tests for the accessibility violations database migration."""

    def inserted_report(
        self, metric_name: str = "Accessibility violations", metric_unit: str = "accessibility violations", **kwargs
    ):
        """Return a report as it is expected to have been inserted into the reports collection."""
        return super().inserted_report(
            metric_type="violations", metric_name=metric_name, metric_unit=metric_unit, **kwargs
        )

    def test_report_without_accessibility_metrics(self):
        """Test that the migration succeeds with reports, but without accessibility metrics."""
        self.database.reports.find.return_value = [self.existing_report(metric_type="loc")]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_accessibility_metric(self):
        """Test that the migration succeeds with an accessibility metric."""
        self.database.reports.find.return_value = [self.existing_report(metric_type="accessibility")]
        perform_migrations(self.database)
        self.check_inserted_report(self.inserted_report())

    def test_accessibility_metric_with_name_and_unit(self):
        """Test that the migration succeeds with an accessibility metric, and existing name and unit are kept."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="accessibility", metric_name="name", metric_unit="unit"),
        ]
        perform_migrations(self.database)
        self.check_inserted_report(self.inserted_report(metric_name="name", metric_unit="unit"))

    def test_report_with_accessibility_metric_and_other_types(self):
        """Test that the migration succeeds with an accessibility metric and other metric types."""
        report = self.existing_report(metric_type="accessibility")
        report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = {"type": "violations"}
        report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID3] = {"type": "security_warnings"}
        self.database.reports.find.return_value = [report]
        perform_migrations(self.database)
        inserted_report = self.inserted_report()
        inserted_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = {"type": "violations"}
        inserted_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID3] = {"type": "security_warnings"}
        self.check_inserted_report(inserted_report)


class BranchParameterTest(MigrationTestCase):
    """Unit tests for the branch parameter database migration."""

    def test_report_without_branch_parameter(self):
        """Test that the migration succeeds with reports, but without metrics with a branch parameter."""
        self.database.reports.find.return_value = [self.existing_report(metric_type="loc")]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_non_empty_branch_parameter(self):
        """Test that the migration succeeds when the branch parameter is not empty."""
        self.database.reports.find.return_value = [
            self.existing_report(
                metric_type="loc",
                sources={SOURCE_ID: {"type": "sonarqube", "parameters": {"branch": "main"}}},
            )
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_branch_parameter_without_value(self):
        """Test that the migration succeeds when a source has an empty branch parameter."""
        sources = {
            SOURCE_ID: {"type": "gitlab", "parameters": {"branch": ""}},
            SOURCE_ID2: {"type": "cloc", "parameters": {"branch": ""}},
        }
        report = self.existing_report(metric_type="source_up_to_dateness", sources=sources)
        self.database.reports.find.return_value = [report]
        perform_migrations(self.database)
        inserted_sources = {
            SOURCE_ID: {"type": "gitlab", "parameters": {"branch": "master"}},
            SOURCE_ID2: {"type": "cloc", "parameters": {"branch": ""}},
        }
        self.check_inserted_report(self.inserted_report(metric_type="source_up_to_dateness", sources=inserted_sources))


class SourceParameterHashMigrationTest(MigrationTestCase):
    """Unit tests for the source parameter hash database migration."""

    def test_report_with_sources_without_source_parameter_hash(self):
        """Test a report with sources and measurements."""
        self.database.measurements.find_one.return_value = {"_id": "id", "metric_uuid": METRIC_ID}
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="loc", sources={SOURCE_ID: {"type": "cloc"}})
        ]
        perform_migrations(self.database)
        inserted_measurement = {"metric_uuid": METRIC_ID, "source_parameter_hash": "8c3b464958e9ad0f20fb2e3b74c80519"}
        self.database.measurements.replace_one.assert_called_once_with({"_id": "id"}, inserted_measurement)

    def test_report_without_sources(self):
        """Test a report without sources."""
        self.database.reports.find.return_value = [self.existing_report(metric_type="loc")]
        perform_migrations(self.database)
        self.database.measurements.replace_one.assert_not_called()

    def test_metric_without_measurement(self):
        """Test a metric without measurements."""
        self.database.measurements.find_one.return_value = None
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="loc", sources={SOURCE_ID: {"type": "cloc"}})
        ]
        perform_migrations(self.database)
        self.database.measurements.replace_one.assert_not_called()


class CIEnvironmentTest(MigrationTestCase):
    """Unit tests for the CI-environment subject type database migration."""

    def inserted_report(self, **kwargs):
        """Extend to set the subject type to development environment."""
        report = super().inserted_report(**kwargs)
        report["subjects"][SUBJECT_ID]["type"] = "development_environment"
        return report

    def test_report_without_ci_environment(self):
        """Test that the migration succeeds without CI-environment subject."""
        self.database.reports.find.return_value = [self.existing_report(metric_type="failed_jobs")]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_ci_environment(self):
        """Test that the migration succeeds with CI-environment subject."""
        report = self.existing_report(metric_type="failed_jobs")
        report["subjects"][SUBJECT_ID]["type"] = "ci"
        self.database.reports.find.return_value = [report]
        perform_migrations(self.database)
        inserted_report = self.inserted_report(metric_type="failed_jobs")
        inserted_report["subjects"][SUBJECT_ID]["name"] = "CI-environment"
        inserted_report["subjects"][SUBJECT_ID]["description"] = "A continuous integration environment."
        self.check_inserted_report(inserted_report)

    def test_ci_environment_with_title_and_subtitle(self):
        """Test that the migration succeeds with an CI-environment subject, and existing title and subtitle are kept."""
        report = self.existing_report(metric_type="failed_jobs")
        report["subjects"][SUBJECT_ID]["type"] = "ci"
        report["subjects"][SUBJECT_ID]["name"] = "CI"
        report["subjects"][SUBJECT_ID]["description"] = "My CI"
        self.database.reports.find.return_value = [report]
        perform_migrations(self.database)
        inserted_report = self.inserted_report(metric_type="failed_jobs")
        inserted_report["subjects"][SUBJECT_ID]["name"] = "CI"
        inserted_report["subjects"][SUBJECT_ID]["description"] = "My CI"
        self.check_inserted_report(inserted_report)


class SonarQubeParameterTest(MigrationTestCase):
    """Unit tests for the SonarQube parameter database migration."""

    def sources(self, source_type: str = "sonarqube", **parameters):
        """Create the sources fixture."""
        return {SOURCE_ID: {"type": source_type, "parameters": {"branch": "main", **parameters}}}

    def test_report_without_severity_or_types_parameter(self):
        """Test that the migration succeeds when the SonarQube source has no severity or types parameter."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="violations", sources=self.sources()),
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_violation_metric_but_no_sonarqube(self):
        """Test that the migration succeeds when a violations metric has no SonarQube sources."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="violations", sources=self.sources("sarif")),
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_severity_parameter(self):
        """Test that the migration succeeds when the SonarQube source has a severity parameter."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="violations", sources=self.sources(severities=["info"])),
        ]
        perform_migrations(self.database)
        inserted_report = self.inserted_report(
            metric_type="violations",
            sources=self.sources(impact_severities=["low"]),
        )
        self.check_inserted_report(inserted_report)

    def test_report_with_multiple_old_severity_values_that_map_to_the_same_new_value(self):
        """Test a severity parameter with multiple old values that map to the same new value."""
        reports = [self.existing_report(metric_type="violations", sources=self.sources(severities=["info", "minor"]))]
        self.database.reports.find.return_value = reports
        perform_migrations(self.database)
        inserted_report = self.inserted_report(
            metric_type="violations",
            sources=self.sources(impact_severities=["low"]),
        )
        self.check_inserted_report(inserted_report)

    @disable_logging
    def test_report_with_unknown_old_severity_values(self):
        """Test that unknown severity parameter values are ignored."""
        sources = self.sources(severities=["info", ""])
        sources[SOURCE_ID2] = {"type": "sonarqube", "parameters": {"branch": "main", "severities": ["foo"]}}
        self.database.reports.find.return_value = [self.existing_report(metric_type="violations", sources=sources)]
        perform_migrations(self.database)
        inserted_sources = self.sources(impact_severities=["low"])
        inserted_sources[SOURCE_ID2] = {"type": "sonarqube", "parameters": {"branch": "main"}}
        inserted_report = self.inserted_report(metric_type="violations", sources=inserted_sources)
        self.check_inserted_report(inserted_report)

    def test_report_with_types_parameter(self):
        """Test that the migration succeeds when the SonarQube source has a types parameter."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="violations", sources=self.sources(types=["bug"])),
        ]
        perform_migrations(self.database)
        inserted_report = self.inserted_report(
            metric_type="violations",
            sources=self.sources(impacted_software_qualities=["reliability"]),
        )
        self.check_inserted_report(inserted_report)

    def test_report_with_types_parameter_without_values(self):
        """Test that the migration succeeds when the SonarQube source has a types parameter without values."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="violations", sources=self.sources(types=[])),
        ]
        perform_migrations(self.database)
        self.check_inserted_report(self.inserted_report(metric_type="violations", sources=self.sources()))

    def test_report_with_security_types_parameter(self):
        """Test that the migration succeeds when the SonarQube source has a security types parameter."""
        self.database.reports.find.return_value = [
            self.existing_report(
                metric_type="security_warnings",
                sources=self.sources(security_types=["security_hotspot", "vulnerability"]),
            ),
        ]
        perform_migrations(self.database)
        inserted_sources = self.sources(security_types=["issue with security impact", "security hotspot"])
        inserted_report = self.inserted_report(metric_type="security_warnings", sources=inserted_sources)
        self.check_inserted_report(inserted_report)

    def test_report_with_security_types_parameter_without_values(self):
        """Test that the migration succeeds when the SonarQube source has a security types parameter without values."""
        reports = [self.existing_report(metric_type="security_warnings", sources=self.sources(security_types=[]))]
        self.database.reports.find.return_value = reports
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()


class TestCasesManualNumberTest(MigrationTestCase):
    """Unit tests for the test cases manual number source migration."""

    def sources(self, source_type: str = "manual_number", source_type2: str = ""):
        """Create the sources fixture."""
        sources = {SOURCE_ID: {"type": source_type}}
        if source_type2:
            sources[SOURCE_ID2] = {"type": source_type2}
        return sources

    def test_report_with_test_cases_and_jira_source(self):
        """Test that the other sources are not removed."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="test_cases", sources=self.sources("jira")),
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_test_cases_and_manual_number_source(self):
        """Test that the manual number source is removed."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="test_cases", sources=self.sources()),
        ]
        perform_migrations(self.database)
        self.check_inserted_report(self.inserted_report(metric_type="test_cases", sources={}))

    def test_report_with_test_cases_and_jira_and_manual_number_source(self):
        """Test that the manual number source is removed."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="test_cases", sources=self.sources("jira", "manual_number")),
        ]
        perform_migrations(self.database)
        self.check_inserted_report(self.inserted_report(metric_type="test_cases", sources=self.sources("jira")))


class UnmergedToInactiveBranchesTest(MigrationTestCase):
    """Unit tests for the unmerged to inactive branches migration."""

    def setUp(self):
        """Create test fixtures."""
        super().setUp()
        self.sources = {SOURCE_ID: {"type": "gitlab", "parameters": {"project": "namespace/project"}}}
        self.expected_sources = {
            SOURCE_ID: {
                "type": "gitlab",
                "parameters": {"project_or_group": "namespace/project", "branch_merge_status": ["unmerged"]},
            }
        }

    def test_report_with_unmerged_branches_metric(self):
        """Test that an unmerged branches metric is migrated."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="unmerged_branches", sources=self.sources),
        ]
        perform_migrations(self.database)
        inserted_report = self.inserted_report(
            metric_type="inactive_branches",
            metric_name="Unmerged branches",
            sources=self.expected_sources,
        )
        self.check_inserted_report(inserted_report)

    def test_report_with_unmerged_branches_metric_with_name(self):
        """Test that the metric name is not changed when migrating the type."""
        metric_name = "Old branches"
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="unmerged_branches", metric_name=metric_name, sources=self.sources),
        ]
        perform_migrations(self.database)
        inserted_report = self.inserted_report(
            metric_type="inactive_branches",
            metric_name=metric_name,
            sources=self.expected_sources,
        )
        self.check_inserted_report(inserted_report)


class ProjectToProjectOrGroupParameterTest(MigrationTestCase):
    """Unit tests for the project to project-or-group GitLab parameter migration."""

    def setUp(self):
        """Create test fixtures."""
        super().setUp()
        self.sources = {
            SOURCE_ID: {"type": "gitlab", "parameters": {"project": "namespace/project"}},
            SOURCE_ID2: {"type": "azure_devops"},
        }
        self.expected_sources = {
            SOURCE_ID: {"type": "gitlab", "parameters": {"project_or_group": "namespace/project"}},
            SOURCE_ID2: {"type": "azure_devops"},
        }

    def test_report_with_project_parameter(self):
        """Test that an project parameter is migrated."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="inactive_branches", sources=self.sources),
        ]
        perform_migrations(self.database)
        inserted_report = self.inserted_report(metric_type="inactive_branches", sources=self.expected_sources)
        self.check_inserted_report(inserted_report)

    def test_idempotency(self):
        """Test that the project parameter is not migrated when it has been changed already."""
        self.database.reports.find.return_value = [
            self.existing_report(metric_type="inactive_branches", sources=self.expected_sources),
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()


class OWASPDependencyCheckToOWASPDependencyCheckXMLTest(MigrationTestCase):
    """Unit tests for the OWASP Dependency-Check to OWASP Dependency-Check XML migration."""

    def setUp(self):
        """Create test fixtures."""
        super().setUp()
        self.sources = {SOURCE_ID: {"type": "owasp_dependency_check", "parameters": {"url": "https://report"}}}
        self.expected_sources = {
            SOURCE_ID: {"type": "owasp_dependency_check_xml", "parameters": {"url": "https://report"}}
        }

    def test_report_with_owasp_dependency_check_source(self):
        """Test that a OWASP Dependency-Check source is migrated."""
        for metric_type in ("dependencies", "security_warnings", "source_up_to_dateness", "source_version"):
            with self.subTest(metric_type=metric_type):
                existing_report = self.existing_report(metric_type=metric_type, sources=self.sources)
                self.database.reports.find.return_value = [existing_report]
                perform_migrations(self.database)
                inserted_report = self.inserted_report(metric_type="dependencies", sources=self.expected_sources)
                self.check_inserted_report(inserted_report)

    def test_idempotency(self):
        """Test that a migrated OWASP Dependency-Check source is unchanged."""
        for metric_type in ("dependencies", "security_warnings", "source_up_to_dateness", "source_version"):
            with self.subTest(metric_type=metric_type):
                existing_report = self.existing_report(metric_type=metric_type, sources=self.expected_sources)
                self.database.reports.find.return_value = [existing_report]
                perform_migrations(self.database)
                self.database.reports.replace_one.assert_not_called()
