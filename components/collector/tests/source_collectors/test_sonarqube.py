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
        expected_entities = [
            dict(component="a", key="a", message="a", severity="info", type="bug",
                 url="https://sonar/project/issues?id=id&issues=a&open=a&branch=master"),
            dict(component="b", key="b", message="b", severity="major", type="code_smell",
                 url="https://sonar/project/issues?id=id&issues=b&open=b&branch=master")]
        self.assert_measurement(response, value="2", entities=expected_entities)

    def test_commented_out_code(self):
        """Test that the number of lines with commented out code is returned."""
        json = dict(total="2")
        metric = dict(type="commented_out_code", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="2", total="100")

    def test_complex_units(self):
        """Test that the number of lines with commented out code is returned."""
        complex_units_json = dict(total="2")
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        metric = dict(type="complex_units", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_side_effect=[complex_units_json, functions_json] * 2)
        self.assert_measurement(response, value="2", total="4")

    def test_tests(self):
        """Test that the number of tests is returned."""
        json = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="88")

    def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the number of lines to cover are returned."""
        json = dict(
            component=dict(
                measures=[dict(metric="uncovered_lines", value="100"), dict(metric="lines_to_cover", value="1000")]))
        metric = dict(type="uncovered_lines", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="100", total="1000")

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the number of branches to cover are returned."""
        json = dict(
            component=dict(
                measures=[
                    dict(metric="uncovered_conditions", value="10"), dict(metric="conditions_to_cover", value="200")]))
        metric = dict(type="uncovered_branches", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="10", total="200")

    def test_duplicated_lines(self):
        """Test that the number of duplicated lines and the total number of lines are returned."""
        json = dict(
            component=dict(
                measures=[
                    dict(metric="duplicated_lines", value="10"), dict(metric="lines", value="100")]))
        metric = dict(type="duplicated_lines", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="10", total="100")

    def test_many_parameters(self):
        """Test that the number of functions with too many parameters is returned."""
        self.sources["source_id"]["parameters"]["rules"] = ["rule1"]
        many_parameters_json = dict(total="2", issues=[])
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        metric = dict(type="many_parameters", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_side_effect=[many_parameters_json, functions_json] * 2)
        self.assert_measurement(response, value="2", total="4")

    def test_long_units(self):
        """Test that the number of long units is returned."""
        self.sources["source_id"]["parameters"]["rules"] = ["rule1"]
        long_units_json = dict(total="2", issues=[])
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        metric = dict(type="long_units", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_side_effect=[long_units_json, functions_json] * 2)
        self.assert_measurement(response, value="2", total="4")

    def test_source_up_to_dateness(self):
        """Test that the number of days since the last analysis is returned."""
        json = dict(analyses=[dict(date="2019-03-29T14:20:15+0100")])
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        timezone_info = timezone(timedelta(hours=1))
        expected_age = (datetime.now(timezone_info) - datetime(2019, 3, 29, 14, 20, 15, tzinfo=timezone_info)).days
        self.assert_measurement(response, value=str(expected_age))

    def test_suppressed_violations(self):
        """Test that the number of suppressed violations includes both suppressed issues as well as suppressed rules."""
        violations_json = dict(
            total="1", issues=[dict(key="a", message="a", component="a", severity="INFO", type="BUG")])
        wont_fix_json = dict(
            total="1",
            issues=[
                dict(key="b", message="b", component="b", severity="MAJOR", type="CODE_SMELL", resolution="WONTFIX")])
        total_violations_json = dict(total="4")
        metric = dict(type="suppressed_violations", addition="sum", sources=self.sources)
        response = self.collect(
            metric, get_request_json_side_effect=[violations_json, wont_fix_json, total_violations_json] * 2)
        expected_entities = [
            dict(component="a", key="a", message="a", severity="info", type="bug",
                 resolution="", url="https://sonar/project/issues?id=id&issues=a&open=a&branch=master"),
            dict(component="b", key="b", message="b", severity="major", type="code_smell",
                 resolution="won't fix", url="https://sonar/project/issues?id=id&issues=b&open=b&branch=master")]
        self.assert_measurement(response, value="2", total="4", entities=expected_entities)

    def test_loc_returns_ncloc_by_default(self):
        """Test that the number of lines of code is returned."""
        json = dict(component=dict(measures=[dict(metric="ncloc", value="1234")]))
        metric = dict(type="loc", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="1234", total="100")

    def test_loc_all_lines(self):
        """Test that the number of lines of code is returned."""
        self.sources["source_id"]["parameters"]["lines_to_count"] = "all lines"
        json = dict(component=dict(measures=[dict(metric="lines", value="1234")]))
        metric = dict(type="loc", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="1234", total="100")

    def test_ncloc(self):
        """Test that the number of non-commented lines of code is returned."""
        json = dict(component=dict(measures=[dict(metric="ncloc", value="999")]))
        metric = dict(type="ncloc", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="999", total="100")

    def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        json = dict(component=dict(measures=[dict(metric="tests", value="123")]))
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="123", total="123")

    def test_nr_of_skipped_tests(self):
        """Test that the number of skipped tests is returned."""
        json = dict(
            component=dict(measures=[dict(metric="tests", value="123"), dict(metric="skipped_tests", value="4")]))
        self.sources["source_id"]["parameters"]["test_result"] = ["skipped"]
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="4", total="123")

    def test_nr_of_tests_without_tests(self):
        """Test that the collector throws an exception if there are no tests."""
        json = dict(component=dict(measures=[]))
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value=None, total=None, parse_error="KeyError")

    def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        json = dict(component=dict(measures=[dict(metric="test_failures", value="13")]))
        metric = dict(type="failed_tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="13", total="100")
