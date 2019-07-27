"""Unit tests for the Bandit source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class BanditTestCase(SourceCollectorTestCase):
    """Base class for testing Bandit collectors."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="bandit", parameters=dict(url="bandit.json")))


class BanditSecurityWarningsTest(BanditTestCase):
    """Unit tests for the security warning metric."""

    def setUp(self):
        super().setUp()
        self.bandit_json = dict(
            results=[
                dict(
                    filename="src/collectors/cxsast.py",
                    issue_confidence="MEDIUM",
                    issue_severity="LOW",
                    issue_text="Possible hardcoded password: '014DF517-39D1-4453-B7B3-9930C563627C'",
                    line_number=37,
                    more_info="https://bandit/b106_hardcoded_password_funcarg.html",
                    test_id="B106",
                    test_name="hardcoded_password_funcarg")])
        self.metric = dict(type="security_warnings", sources=self.sources, addition="sum")

    def test_warnings(self):
        """Test the number of security warnings."""
        response = self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_value("1", response)
        self.assert_entities(
            [dict(
                location="src/collectors/cxsast.py:37", key="B106:src/collectors/cxsast.py:37",
                issue_text="Possible hardcoded password: '014DF517-39D1-4453-B7B3-9930C563627C'",
                issue_severity="Low", issue_confidence="Medium",
                more_info="https://bandit/b106_hardcoded_password_funcarg.html")],
            response)

    def test_warnings_with_high_severity(self):
        """Test the number of high severity security warnings."""
        self.sources["source_id"]["parameters"]["severities"] = ["high"]
        response = self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_value("0", response)
        self.assert_entities([], response)

    def test_warnings_with_high_confidence(self):
        """Test the number of high confidence security warnings."""
        self.sources["source_id"]["parameters"]["confidence_levels"] = ["high"]
        response = self.collect(self.metric, get_request_json_return_value=self.bandit_json)
        self.assert_value("0", response)
        self.assert_entities([], response)


class BanditSourceUpToDatenessTest(BanditTestCase):
    """Unit tests for the source up to dateness metric."""

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        bandit_json = dict(generated_at="2019-07-12T07:38:47Z")
        response = self.collect(metric, get_request_json_return_value=bandit_json)
        expected_age = (datetime.now() - datetime(2019, 7, 12, 7, 38, 47)).days
        self.assert_value(str(expected_age), response)
