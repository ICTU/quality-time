"""Unit tests for the report routes."""

import unittest
from datetime import datetime
from typing import cast
from unittest.mock import Mock, patch
import copy

from routes.report import (
    delete_report,
    export_report_as_json,
    export_report_as_pdf,
    get_report,
    get_tag_report,
    post_report_attribute,
    post_report_copy,
    post_report_import,
    post_report_new,
)
from server_utilities.functions import asymmetric_encrypt
from server_utilities.type import ReportId

from ..fixtures import JENNY, JOHN, REPORT_ID, REPORT_ID2, SUBJECT_ID, create_report


@patch("bottle.request")
class PostReportAttributeTest(unittest.TestCase):
    """Unit tests for the post report attribute route."""

    def setUp(self):
        """Override to set up a database with a report and a user session."""
        self.database = Mock()
        self.report = dict(_id="id", report_uuid=REPORT_ID, title="Title")
        self.database.reports.find.return_value = [self.report]
        self.database.sessions.find_one.return_value = JOHN
        self.database.datamodels.find_one.return_value = {}
        self.database.measurements.find.return_value = []

    def test_post_report_title(self, request):
        """Test that the report title can be changed."""
        request.json = dict(title="New title")
        self.assertEqual(dict(ok=True), post_report_attribute(REPORT_ID, "title", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(
                uuids=[REPORT_ID],
                email=JOHN["email"],
                description="John changed the title of report 'Title' from 'Title' to 'New title'.",
            ),
            self.report["delta"],
        )

    def test_post_report_layout(self, request):
        """Test that the report layout can be changed."""
        request.json = dict(layout=[dict(x=1, y=2)])
        self.assertEqual(dict(ok=True), post_report_attribute(REPORT_ID, "layout", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID], email=JOHN["email"], description="John changed the layout of report 'Title'."),
            self.report["delta"],
        )


class ReportTest(unittest.TestCase):
    """Unit tests for adding, deleting, and getting reports."""

    def setUp(self):
        """Override to set up a database with a report and a user session."""
        self.private_key = """-----BEGIN PRIVATE KEY-----
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

        self.dsa_private_key = """-----BEGIN PRIVATE KEY-----
MIIBSgIBADCCASsGByqGSM44BAEwggEeAoGBALof0klegL4faacbyvhs4afc2zsk
k917FY0+61bR0iP/4W/Zpm5OYnruGXmEIxe2pHBrpqAFl8gpArpwTIMZQdcZV3Np
/rZn5m8j9wxyJHxZPfnTMNvM0V6xFA/WOpWFxTrhKNghl/Nr01RoLGN2a96q8PPI
F93vKzWmlHAvo4fPAhUAmr55ZB6b4bF94auvyKJrrUWW4hsCgYBTQm1Pgc7Xfzg5
9b4cEw324SHwNPCK1qvNhDaiJmEwhDNN1pTLqDFeJwdlsleFlvhaCp39GdUzykOd
ugLAEWafGAAZnoXqGxXSpER0zvMqDkZARpnP8gvb9wtugKY+n0vcPbLw0dMogsjc
nRds5J/QhcndadsQQ+BckzMM0hAhKQQWAhQR90SPKLVCoLbNBqxPgEMar6I0EA==
-----END PRIVATE KEY-----"""

        self.public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDXSVUXcpWmnbGmroUcTU6CFCJP
50ijM3444z/9tBREoZGsdYOAmE8E3UjHLlfuG5c8xUhPng5jLNSzZIwD83zQJx8C
bI89r7deiVw5mvj7iD0wiObqGwmz1Cbcvul5Z8xclY8t+vkoHgPEjBx06azsYcMV
PvjuXJ8zuyW+Jo6DrwIDAQAB
-----END PUBLIC KEY-----
"""

        self.dsa_public_key = """-----BEGIN PUBLIC KEY-----
MIIBtjCCASsGByqGSM44BAEwggEeAoGBAN2YsbQRxa3noHUehRXbDaTmCQCsBW6D
Gy4Yo/Rzg1O6S4gBrk9/h64V3ZcNzKgh3G73v5nReLJo545vq5ZdglRxVqRzEkvK
ecbRrKJfSL/Ir6+utojcBte9u8mK8VBzOEzu3d9VMXhohnLc8AKJgoVz2VLYboHb
DDqil8n5GA81AhUA1zdcpHIsos80Xr8W67v+zc1NugMCgYBO9ui2yfUJK67P3yKm
5kcD7owtqdrgEWo3zPSU94Dyq83ZKnQCqW4jyNVvLHE8vorfrzQG05yxA27fh9y3
13CqD3+SRs1/bh+OoHTYfOg5nQpd+wmpD1KcliwozSa4UoB6L0HGSsmdfDMnyjY6
57A/6fvkIPfFWwiZqDw/UbvXJAOBhAACgYAClAnMuoF2cRmHIkgx7rkBtQQDUuL+
w+tVREFni2i1NBgXEN18fFRtebuPKJvoY0ISQgR+XPoKsgfnQ7jy8bsoZvrto3CP
pwEguMmZYw493abU3P4d66wDe/sFyNLW0rhIx+sYsQ6YhGVWF46peoFC3Aa2H439
frfI8VlILbIxGw==
-----END PUBLIC KEY-----"""

        self.database = Mock()
        self.database.sessions.find_one.return_value = JENNY
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            subjects=dict(subject_type=dict(name="Subject type")),
            metrics=dict(metric_type=dict(name="Metric type")),
            sources=dict(source_type=dict(name="Source type", parameters={"url": {"type": "not a password"}})),
        )
        self.report = create_report()
        self.database.reports.find.return_value = [self.report]
        self.database.secrets.find_one.return_value = {"public_key": self.public_key, "private_key": self.private_key}
        self.database.measurements.find.return_value = []
        self.options = (
            "emulateScreenMedia=false&goto.timeout=60000&scrollPage=true&waitFor=10000&pdf.scale=0.7&"
            "pdf.margin.top=25&pdf.margin.bottom=25&pdf.margin.left=25&pdf.margin.right=25"
        )

    def test_get_report(self):
        """Test that a report can be retrieved."""
        self.assertEqual(REPORT_ID, get_report(self.database, REPORT_ID)["reports"][0]["report_uuid"])

    def test_get_report_and_info_about_other_reports(self):
        """Test that a report can be retrieved, and that other reports are also returned."""
        self.database.reports.find.return_value.insert(0, dict(_id="id2", report_uuid=REPORT_ID2))
        self.assertEqual(2, len(get_report(self.database, REPORT_ID)["reports"]))

    def test_get_report_missing(self):
        """Test that a report can be retrieved."""
        self.database.reports.find.return_value = []
        self.assertEqual([], get_report(self.database, ReportId("report does not exist"))["reports"])

    def test_add_report(self):
        """Test that a report can be added."""
        self.assertTrue(post_report_new(self.database)["ok"])
        self.database.reports.insert.assert_called_once()
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual("New report", inserted["title"])
        self.assertEqual(
            dict(uuids=[inserted["report_uuid"]], email=JENNY["email"], description="Jenny created a new report."),
            inserted["delta"],
        )

    def test_copy_report(self):
        """Test that a report can be copied."""
        self.assertTrue(post_report_copy(REPORT_ID, self.database)["ok"])
        self.database.reports.insert.assert_called_once()
        inserted_report = self.database.reports.insert.call_args[0][0]
        inserted_report_uuid = inserted_report["report_uuid"]
        self.assertNotEqual(self.report["report_uuid"], inserted_report_uuid)
        self.assertEqual(
            dict(
                uuids=[REPORT_ID, inserted_report_uuid],
                email=JENNY["email"],
                description="Jenny copied the report 'Report'.",
            ),
            inserted_report["delta"],
        )

    @patch("requests.get")
    def test_get_pdf_report(self, requests_get):
        """Test that a PDF version of the report can be retrieved."""
        response = Mock()
        response.content = b"PDF"
        requests_get.return_value = response
        self.assertEqual(b"PDF", export_report_as_pdf(cast(ReportId, "report_uuid")))
        requests_get.assert_called_once_with(
            f"http://renderer:9000/api/render?url=http%3A//www%3A80/report_uuid&{self.options}"
        )

    def test_get_json_report(self):
        """Test that a JSON version of the report can be retrieved with encrypted credentials."""
        expected_report = copy.deepcopy(self.report)
        expected_report["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]["sources"]["source_uuid"][
            "parameters"
        ].pop("password")
        self.database.reports.find_one.return_value = copy.deepcopy(self.report)

        # without provided public key
        exported_report = export_report_as_json(self.database, cast(ReportId, REPORT_ID))
        exported_password = exported_report["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]["sources"][
            "source_uuid"
        ]["parameters"].pop("password")

        self.assertDictEqual(exported_report, expected_report)
        self.assertTrue(isinstance(exported_password, tuple))
        self.assertTrue(len(exported_password) == 2)

    @patch("routes.report.bottle.request")
    def test_get_json_report_with_public_key(self, request):
        """Test that a provided public key can be used to encrypt the passwords."""
        expected_report = copy.deepcopy(self.report)
        expected_report["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]["sources"]["source_uuid"][
            "parameters"
        ].pop("password")

        request.query = {"public_key": self.public_key}
        mocked_report = copy.deepcopy(self.report)
        mocked_report["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]["sources"]["source_uuid"]["parameters"][
            "password"
        ] = [
            "0",
            "1",
        ]  # use a list as password for coverage of the last line
        self.database.reports.find_one.return_value = mocked_report
        exported_report = export_report_as_json(self.database, cast(ReportId, REPORT_ID))
        exported_password = exported_report["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]["sources"][
            "source_uuid"
        ]["parameters"].pop("password")

        self.assertDictEqual(exported_report, expected_report)
        self.assertTrue(isinstance(exported_password, tuple))
        self.assertTrue(len(exported_password) == 2)

    @patch("routes.report.bottle.request")
    def test_get_json_report_with_faulty_public_key(self, request):
        """Test that a faulty public key will raise a typeerror."""
        request.query = {"public_key": self.dsa_public_key}
        mocked_report = copy.deepcopy(self.report)
        mocked_report["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]["sources"]["source_uuid"]["parameters"][
            "password"
        ] = [
            "0",
            "1",
        ]  # use a list as password for coverage of the last line
        self.database.reports.find_one.return_value = mocked_report
        exported_report = export_report_as_json(self.database, cast(ReportId, REPORT_ID))
        self.assertIn("error", exported_report)

    @patch("requests.get")
    def test_get_pdf_tag_report(self, requests_get):
        """Test that a PDF version of a tag report can be retrieved."""
        requests_get.return_value = Mock(content=b"PDF")
        self.assertEqual(b"PDF", export_report_as_pdf(cast(ReportId, "tag-security")))
        requests_get.assert_called_once_with(
            f"http://renderer:9000/api/render?url=http%3A//www%3A80/tag-security&{self.options}"
        )

    def test_delete_report(self):
        """Test that the report can be deleted."""
        self.assertEqual(dict(ok=True), delete_report(REPORT_ID, self.database))
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual(
            dict(uuids=[REPORT_ID], email=JENNY["email"], description="Jenny deleted the report 'Report'."),
            inserted["delta"],
        )

    @patch("bottle.request")
    def test_post_report_import(self, request):
        """Test that a report is imported correctly."""
        mocked_report = copy.deepcopy(self.report)
        mocked_report["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]["sources"]["source_uuid"]["parameters"][
            "password"
        ] = asymmetric_encrypt(self.public_key, "test_message")
        request.json = mocked_report
        post_report_import(self.database)
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual("Title", inserted["title"])
        self.assertEqual("report_uuid", inserted["report_uuid"])

    @patch("server_utilities.functions.datetime")
    def test_get_tag_report(self, date_time):
        """Test that a tag report can be retrieved."""
        date_time.now.return_value = now = datetime.now()
        self.database.reports.find.return_value = [
            dict(
                _id="id",
                report_uuid=REPORT_ID,
                title="Report",
                subjects={
                    "subject_without_metrics": dict(metrics={}),
                    SUBJECT_ID: dict(
                        name="Subject",
                        type="subject_type",
                        metrics=dict(
                            metric_with_tag=dict(type="metric_type", tags=["tag"]),
                            metric_without_tag=dict(type="metric_type", tags=["other tag"]),
                        ),
                    ),
                },
            )
        ]
        self.assertDictEqual(
            dict(
                summary=dict(red=0, green=0, yellow=0, grey=0, white=1),
                summary_by_tag=dict(tag=dict(red=0, green=0, yellow=0, grey=0, white=1)),
                summary_by_subject={SUBJECT_ID: dict(red=0, green=0, yellow=0, grey=0, white=1)},
                title='Report for tag "tag"',
                subtitle="Note: tag reports are read-only",
                report_uuid="tag-tag",
                timestamp=now.replace(microsecond=0).isoformat(),
                subjects={
                    SUBJECT_ID: dict(
                        name="Report / Subject",
                        type="subject_type",
                        metrics=dict(
                            metric_with_tag=dict(
                                status=None,
                                value=None,
                                scale="count",
                                recent_measurements=[],
                                type="metric_type",
                                tags=["tag"],
                            )
                        ),
                    )
                },
            ),
            get_tag_report("tag", self.database),
        )
