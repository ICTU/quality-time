"""Model transformation unit tests."""

from model.report import Report
from model.transformations import (
    CREDENTIALS_REPLACEMENT_TEXT,
    SOURCE_TYPES_WITHOUT_LOCATION,
    add_source_locations,
    change_source_parameter,
    decrypt_credentials,
    encrypt_credentials,
    hide_credentials,
    replace_report_uuids,
)

from tests.base import DataModelTestCase
from tests.fixtures import (
    METRIC_ID,
    METRIC_ID2,
    REPORT_ID,
    SOURCE_ID,
    SOURCE_ID2,
    SOURCE_LOCATION_ID,
    SUBJECT_ID,
    create_report,
)
from utils.type import SourceContext

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDXSVUXcpWmnbGmroUcTU6CFCJP
50ijM3444z/9tBREoZGsdYOAmE8E3UjHLlfuG5c8xUhPng5jLNSzZIwD83zQJx8C
bI89r7deiVw5mvj7iD0wiObqGwmz1Cbcvul5Z8xclY8t+vkoHgPEjBx06azsYcMV
PvjuXJ8zuyW+Jo6DrwIDAQAB
-----END PUBLIC KEY-----
"""

PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBANdJVRdylaadsaau
hRxNToIUIk/nSKMzfjjjP/20FEShkax1g4CYTwTdSMcuV+4blzzFSE+eDmMs1LNk
jAPzfNAnHwJsjz2vt16JXDma+PuIPTCI5uobCbPUJty+6XlnzFyVjy36+SgeA8SM
HHTprOxhwxU++O5cnzO7Jb4mjoOvAgMBAAECgYEAr9gMErzbE16Wroi53OYgDAua
Ax3srLDwllK3/+fI7k3yCKVrpevCDz0XpulplOkgXNjfOXjmU4dYrLahztBgzrwt
KzA7H8XylleIbuk7wUJ8jD+1dzxgu/ZB+iLzUla8r9/MmdhAzELmYBc9hIEWl6FW
2BlQxmLNbOj2kh/aWoECQQD4GyLDzxEFVBPYYo+Ut3T05a0IlCnCSKU6saDSuFFG
GhiM1HQMAnnuC3okgVpAOA7Rn2z9xMqLcdiv+Amnzh3hAkEA3iLgQUwMj6v97Jkb
KFxQazzkOmgMKFGH2MbZGGwDDva1QlD9awjBW0aj4nUHNsUob6LVJCbCocQFSNDu
eXgzjwJATSg7NoPFuk98YHW+SzSGZcarehiBqA7pe4hUCFQTymZBLkK/2CBJBPOC
x6mGhKQqT5xxy7WQe68rAQZ1Ej9yYQJAbgd8aRuQRUH+HsmfyBghxVx99+g9zWLF
FT05n30w7qKJGfYf8Hp/vAR7fNpW3mw+IT3YsXV5hsMfkvfah9RgRQJAVGysMIfp
eX94CsogDhIWSaXreAfpcWQu1Dg5FCmpZTGRJps2x52CPq5icgBZeIODElIvkJbn
JqqQtg8ZsTm6Pw==
-----END PRIVATE KEY-----
"""


def create_old_structure_report() -> dict:
    """Return a report with the old structure, i.e. with the location parameters in the source parameters."""
    return {
        "report_uuid": REPORT_ID,
        "title": "Report",
        "subjects": {
            SUBJECT_ID: {
                "name": "Subject",
                "type": "software",
                "metrics": {
                    METRIC_ID: {
                        "name": "Metric",
                        "type": "violations",
                        "sources": {
                            SOURCE_ID: {
                                "type": "sonarqube",
                                "name": "Source",
                                "parameters": {"url": "https://url", "password": "password", "tags": ["security"]},  # nosec
                            },
                        },
                    },
                },
            },
        },
    }


class HideCredentialsTest(DataModelTestCase):
    """Unit tests for the hide credentials transformation."""

    def setUp(self) -> None:
        """Override to set up the report fixture."""
        self.report = create_report()
        self.source_location = self.report["source_locations"][SOURCE_LOCATION_ID]
        self.issue_tracker_parameters = self.report["issue_tracker"]["parameters"]

    def test_hide_source_location_credentials(self):
        """Test that the source location credentials are hidden."""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual(CREDENTIALS_REPLACEMENT_TEXT, self.source_location["password"])

    def test_hide_source_credentials(self):
        """Test that source credentials in old-structure reports are hidden, needed for time traveling."""
        old_report = create_old_structure_report()
        hide_credentials(self.DATA_MODEL, old_report)
        source_parameters = old_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"]
        self.assertEqual(CREDENTIALS_REPLACEMENT_TEXT, source_parameters["password"])

    def test_hide_issue_tracker_credentials(self):
        """Test that the issue tracker credentials are hidden."""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual(CREDENTIALS_REPLACEMENT_TEXT, self.issue_tracker_parameters["password"])

    def test_do_not_hide_empty_source_location_credentials(self):
        """Test that empty source location credentials are not replaced with a placeholder.

        This is needed because users cannot see the difference between a masked credential and a masked empty
        credential in the UI. If we mask empty credentials the users won't be able to tell that they did successfully
        clear a credential (because it looks the same as an existing credential) and complain there is a bug.
        """
        self.source_location["password"] = ""  # nosec
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual("", self.source_location["password"])

    def test_do_not_hide_empty_issue_tracker_credentials(self):
        """Test that empty issue tracker credentials are not replaced with a placeholder.

        This is needed because users cannot see the difference between a masked credential and a masked empty
        credential in the UI. If we mask empty credentials the users won't be able to tell that they did successfully
        clear a credential (because it looks the same as an existing credential) and complain there is a bug.
        """
        self.issue_tracker_parameters["private_token"] = ""  # nosec
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual("", self.issue_tracker_parameters["private_token"])

    def test_hide_credentials_when_report_has_no_issue_tracker(self):
        """Test that hiding credentials works on a report that has no issue tracker."""
        del self.report["issue_tracker"]
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual(CREDENTIALS_REPLACEMENT_TEXT, self.source_location["password"])

    def test_hide_credentials_when_issue_tracker_has_no_parameters(self):
        """Test that hiding credentials works on a report whose issue tracker has no parameters yet."""
        self.report["issue_tracker"] = {"type": "jira"}
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual(CREDENTIALS_REPLACEMENT_TEXT, self.source_location["password"])


class EncryptDecryptCredentialsTest(DataModelTestCase):
    """Unit tests for the encrypt and decrypt credentials transformations."""

    def setUp(self) -> None:
        """Override to set up the report fixture."""
        self.report = create_report()
        self.source_location = self.report["source_locations"][SOURCE_LOCATION_ID]

    def test_encrypt_and_decrypt_source_location_credentials(self):
        """Test that the source location credentials can be encrypted and decrypted."""
        encrypt_credentials(PUBLIC_KEY, self.report)
        self.assertIsInstance(self.source_location["password"], tuple)
        self.assertIsInstance(self.report["issue_tracker"]["parameters"]["password"], tuple)
        self.assertTrue(decrypt_credentials(PRIVATE_KEY, self.report))
        self.assertEqual("password", self.source_location["password"])
        self.assertEqual("secret", self.report["issue_tracker"]["parameters"]["password"])

    def test_decrypt_source_location_credentials_with_wrong_key(self):
        """Test that decrypting the source location credentials with a malformed credential fails."""
        self.source_location["password"] = ("not_properly_encrypted==", "test_message")  # nosec
        self.assertFalse(decrypt_credentials(PRIVATE_KEY, self.report))
        self.assertNotIn("password", self.source_location)


class ChangeSourceParameterTest(DataModelTestCase):
    """Unit tests for the change source parameter transformation."""

    def test_change_parameter(self):
        """Test changing a source parameter."""
        report = Report(self.DATA_MODEL, create_report())
        subject = report.subjects_dict[SUBJECT_ID]
        metric = report.metrics_dict[METRIC_ID]
        source = metric.sources_dict[SOURCE_ID]
        context = SourceContext(source=source, metric=metric, subject=subject, report=report)
        changed_ids = change_source_parameter(context, "tags", ["safety"])
        self.assertEqual([REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID], changed_ids)
        self.assertEqual(["safety"], source["parameters"]["tags"])


class SourceTypesWithoutLocationTest(DataModelTestCase):
    """Unit tests for the source types without location constant."""

    def test_source_types_without_location(self):
        """Test that the source types without a url parameter don't have source locations."""
        self.assertEqual({"calendar", "manual_number", "manual_version"}, set(SOURCE_TYPES_WITHOUT_LOCATION))


class AddSourceLocationsTest(DataModelTestCase):
    """Unit tests for the add source locations transformation."""

    def test_add_source_locations(self):
        """Test that the location parameters are moved to a source location at the report level."""
        report = create_old_structure_report()
        self.assertEqual("add source locations", add_source_locations(report))
        location_uuid, location = next(iter(report["source_locations"].items()))
        self.assertEqual(
            {
                "location_name": "Source",
                "source_type": "sonarqube",
                "url": "https://url",
                "landing_url": "",
                "username": "",
                "password": "password",  # nosec
                "private_token": "",
            },
            location,
        )
        source = report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        self.assertEqual(location_uuid, source["source_location"])
        self.assertEqual({"tags": ["security"]}, source["parameters"])

    def test_add_source_locations_is_idempotent(self):
        """Test that reports that already have source locations are not changed."""
        report = create_report()
        expected_report = create_report()
        self.assertEqual("", add_source_locations(report))
        self.assertEqual(expected_report, report)

    def test_add_source_locations_deduplicates_equal_locations(self):
        """Test that sources with equal names, types, and location parameters share one source location."""
        report = create_old_structure_report()
        sources = report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"]
        sources[SOURCE_ID2] = {
            "type": "sonarqube",
            "name": "Source",
            "parameters": {"url": "https://url", "password": "password"},  # nosec
        }
        add_source_locations(report)
        self.assertEqual(1, len(report["source_locations"]))
        self.assertEqual(sources[SOURCE_ID]["source_location"], sources[SOURCE_ID2]["source_location"])

    def test_add_source_locations_does_not_deduplicate_different_locations(self):
        """Test that sources with different location parameters get different source locations."""
        report = create_old_structure_report()
        sources = report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"]
        sources[SOURCE_ID2] = {
            "type": "sonarqube",
            "name": "Source",
            "parameters": {"url": "https://other-url", "password": "password"},  # nosec
        }
        add_source_locations(report)
        self.assertEqual(2, len(report["source_locations"]))
        self.assertNotEqual(sources[SOURCE_ID]["source_location"], sources[SOURCE_ID2]["source_location"])

    def test_add_source_locations_skips_source_types_without_location(self):
        """Test that sources of types without location parameters don't get a source location."""
        report = create_old_structure_report()
        report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = {
            "name": "Metric 2",
            "type": "calendar",
            "sources": {SOURCE_ID2: {"type": "calendar", "parameters": {"date": "2026-01-01"}}},
        }
        add_source_locations(report)
        self.assertEqual(1, len(report["source_locations"]))
        source = report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2]["sources"][SOURCE_ID2]
        self.assertNotIn("source_location", source)
        self.assertEqual({"date": "2026-01-01"}, source["parameters"])


class ReplaceReportUuidsTest(DataModelTestCase):
    """Unit tests for the replace report uuids transformation."""

    def test_replace_report_uuids(self):
        """Test that the report, subject, metric, source, and source location uuids are replaced."""
        report = create_report()
        replace_report_uuids(report)
        self.assertNotEqual(REPORT_ID, report["report_uuid"])
        new_location_uuid, new_location = next(iter(report["source_locations"].items()))
        self.assertNotEqual(SOURCE_LOCATION_ID, new_location_uuid)
        self.assertEqual("https://url", new_location["url"])
        new_subject = next(iter(report["subjects"].values()))
        new_metric = next(iter(new_subject["metrics"].values()))
        new_source = next(iter(new_metric["sources"].values()))
        self.assertEqual(new_location_uuid, new_source["source_location"])
