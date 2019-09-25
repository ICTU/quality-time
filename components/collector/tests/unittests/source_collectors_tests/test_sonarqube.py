"""Unit tests for the SonarQube source."""

from datetime import datetime, timedelta, timezone

from .source_collector_test_case import SourceCollectorTestCase


class SonarQubeTest(SourceCollectorTestCase):
    """Unit tests for the SonarQube metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="sonarqube", parameters=dict(url="https://sonar", component="id")))

    def test_violations(self):
        """Test that the number of violations is returned."""
        json = dict(
            total="2",
            issues=[
                dict(key="a", message="a", component="a", severity="INFO", type="BUG"),
                dict(key="b", message="b", component="b", severity="MAJOR", type="CODE_SMELL")])
        metric = dict(type="violations", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_entities(
            [
                dict(component="a", key="a", message="a", severity="info", type="bug",
                     url="https://sonar/project/issues?id=id&issues=a&open=a"),
                dict(component="b", key="b", message="b", severity="major", type="code_smell",
                     url="https://sonar/project/issues?id=id&issues=b&open=b")
            ],
            response)
        self.assert_value("2", response)

    def test_tests(self):
        """Test that the number of tests is returned."""
        json = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("88", response)

    def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the number of lines to cover are returned."""
        json = dict(
            component=dict(
                measures=[dict(metric="uncovered_lines", value="100"), dict(metric="lines_to_cover", value="1000")]))
        metric = dict(type="uncovered_lines", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("100", response)
        self.assert_total("1000", response)

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the number of branches to cover are returned."""
        json = dict(
            component=dict(
                measures=[
                    dict(metric="uncovered_conditions", value="10"), dict(metric="conditions_to_cover", value="200")]))
        metric = dict(type="uncovered_branches", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("10", response)
        self.assert_total("200", response)

    def test_duplicated_lines(self):
        """Test that the number of duplicated lines and the total number of lines are returned."""
        json = dict(
            component=dict(
                measures=[
                    dict(metric="duplicated_lines", value="10"), dict(metric="lines", value="100")]))
        metric = dict(type="duplicated_lines", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("10", response)
        self.assert_total("100", response)

    def test_long_units(self):
        """Test that the number of long units is returned."""
        self.sources["source_id"]["parameters"]["rules"] = ["rule1"]
        json = dict(total="2", issues=[])
        metric = dict(type="long_units", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("2", response)

    def test_source_up_to_dateness(self):
        """Test that the number of days since the last analysis is returned."""
        json = dict(analyses=[dict(date="2019-03-29T14:20:15+0100")])
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        tzinfo = timezone(timedelta(hours=1))
        expected_age = (datetime.now(tzinfo) - datetime(2019, 3, 29, 14, 20, 15, tzinfo=tzinfo)).days
        self.assert_value(str(expected_age), response)

    def test_suppressed_violations(self):
        """Test that the number of suppressed violations includes both suppressed issues as well as suppressed rules."""
        json = 2 * [
            dict(total="1",
                 issues=[dict(key="a", message="a", component="a", severity="INFO", type="BUG")]),
            dict(total="1",
                 issues=[dict(key="b", message="b", component="b", severity="MAJOR", type="CODE_SMELL",
                              resolution="WONTFIX")])]
        metric = dict(type="suppressed_violations", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_side_effect=json)
        self.assert_entities(
            [
                dict(component="a", key="a", message="a", severity="info", type="bug",
                     resolution="", url="https://sonar/project/issues?id=id&issues=a&open=a"),
                dict(component="b", key="b", message="b", severity="major", type="code_smell",
                     resolution="won't fix", url="https://sonar/project/issues?id=id&issues=b&open=b")
            ],
            response)
        self.assert_value("2", response)

    def test_loc(self):
        """Test that the number of lines of code is returned."""
        json = dict(component=dict(measures=[dict(metric="lines", value="1234")]))
        metric = dict(type="loc", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("1234", response)
        self.assert_total("100", response)

    def test_ncloc(self):
        """Test that the number of non-commented lines of code is returned."""
        json = dict(component=dict(measures=[dict(metric="ncloc", value="999")]))
        metric = dict(type="ncloc", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("999", response)
        self.assert_total("100", response)

    def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        json = dict(component=dict(measures=[dict(metric="tests", value="123")]))
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("123", response)
        self.assert_total("100", response)

    def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        json = dict(component=dict(measures=[dict(metric="test_failures", value="13")]))
        metric = dict(type="failed_tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("13", response)
        self.assert_total("100", response)

