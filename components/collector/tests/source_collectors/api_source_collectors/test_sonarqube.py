"""Unit tests for the SonarQube source."""

from datetime import datetime, timedelta, timezone

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class SonarQubeTest(SourceCollectorTestCase):
    """Unit tests for the SonarQube metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="sonarqube", parameters=dict(url="https://sonar", component="id", types=["bug", "code_smell"])))
        self.tests_landing_url = "https://sonar/component_measures?id=id&metric=tests&branch=master"
        self.issues_landing_url = "https://sonar/project/issues?id=id&resolved=false&branch=master"

    async def test_violations(self):
        """Test that the number of violations is returned."""
        json = dict(
            total="2",
            issues=[
                dict(key="a", message="a", component="a", severity="INFO", type="BUG"),
                dict(key="b", message="b", component="b", severity="MAJOR", type="CODE_SMELL")])
        metric = dict(type="violations", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        expected_entities = [
            dict(component="a", key="a", message="a", severity="info", type="bug",
                 url="https://sonar/project/issues?id=id&issues=a&open=a&branch=master"),
            dict(component="b", key="b", message="b", severity="major", type="code_smell",
                 url="https://sonar/project/issues?id=id&issues=b&open=b&branch=master")]
        self.assert_measurement(response, value="2", entities=expected_entities, landing_url=self.issues_landing_url)

    async def test_security_hotspots(self):
        """Test that the number of security hotspots is returned."""
        self.sources["source_id"]["parameters"]["types"] = ["security_hotspot"]
        json = dict(
            total="2",
            issues=[
                dict(key="a", message="a", component="a", type="SECURITY_HOTSPOT"),
                dict(key="b", message="b", component="b", type="SECURITY_HOTSPOT")])
        metric = dict(type="violations", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        expected_entities = [
            dict(component="a", key="a", message="a", severity="no severity", type="security_hotspot",
                 url="https://sonar/project/issues?id=id&issues=a&open=a&branch=master"),
            dict(component="b", key="b", message="b", severity="no severity", type="security_hotspot",
                 url="https://sonar/project/issues?id=id&issues=b&open=b&branch=master")]
        self.assert_measurement(response, value="2", entities=expected_entities, landing_url=self.issues_landing_url)

    async def test_bugs_and_security_hotspots(self):
        """Test that the number of bugs and security hotspots is returned."""
        self.sources["source_id"]["parameters"]["types"] = ["bug", "security_hotspot"]
        bug_json = dict(total="1", issues=[dict(key="a", message="a", component="a", severity="MAJOR", type="BUG")])
        hotspot_json = dict(total="1", issues=[dict(key="b", message="b", component="b", type="SECURITY_HOTSPOT")])
        metric = dict(type="violations", addition="sum", sources=self.sources)
        response = await self.collect(
            metric, get_request_json_side_effect=[bug_json, bug_json, hotspot_json, hotspot_json])
        expected_entities = [
            dict(component="a", key="a", message="a", severity="major", type="bug",
                 url="https://sonar/project/issues?id=id&issues=a&open=a&branch=master"),
            dict(component="b", key="b", message="b", severity="no severity", type="security_hotspot",
                 url="https://sonar/project/issues?id=id&issues=b&open=b&branch=master")]
        self.assert_measurement(response, value="2", entities=expected_entities, landing_url=self.issues_landing_url)

    async def test_commented_out_code(self):
        """Test that the number of lines with commented out code is returned."""
        json = dict(total="2")
        metric = dict(type="commented_out_code", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="2", total="100",
            landing_url=f"{self.issues_landing_url}&rules=abap:S125,apex:S125,c:CommentedCode,cpp:CommentedCode,"
                        "flex:CommentedCode,csharpsquid:S125,javascript:CommentedCode,kotlin:S125,objc:CommentedCode,"
                        "php:S125,plsql:S125,python:S125,scala:S125,squid:CommentedOutCodeLine,swift:S125,"
                        "typescript:S125,Web:AvoidCommentedOutCodeCheck,xml:S125")

    async def test_complex_units(self):
        """Test that the number of lines with commented out code is returned."""
        complex_units_json = dict(total="2")
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        metric = dict(type="complex_units", addition="sum", sources=self.sources)
        response = await self.collect(
            metric,
            get_request_json_side_effect=[
                {}, complex_units_json, functions_json, complex_units_json, functions_json, complex_units_json])
        self.assert_measurement(
            response, value="2", total="4",
            landing_url=f"{self.issues_landing_url}&rules=csharpsquid:S1541,csharpsquid:S3776,flex:FunctionComplexity,"
                        "javascript:FunctionComplexity,javascript:S3776,go:S3776,kotlin:S3776,php:S1541,php:S3776,"
                        "python:FunctionComplexity,python:S3776,ruby:S3776,scala:S3776,squid:MethodCyclomatic"
                        "Complexity,squid:S3776,typescript:S1541,typescript:S3776,vbnet:S1541,vbnet:S3776")

    async def test_tests(self):
        """Test that the number of tests is returned."""
        json = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="88", landing_url=self.tests_landing_url)

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the number of lines to cover are returned."""
        json = dict(
            component=dict(
                measures=[dict(metric="uncovered_lines", value="100"), dict(metric="lines_to_cover", value="1000")]))
        metric = dict(type="uncovered_lines", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="100", total="1000",
            landing_url="https://sonar/component_measures?id=id&metric=uncovered_lines&branch=master")

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the number of branches to cover are returned."""
        json = dict(
            component=dict(
                measures=[
                    dict(metric="uncovered_conditions", value="10"), dict(metric="conditions_to_cover", value="200")]))
        metric = dict(type="uncovered_branches", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="10", total="200",
            landing_url="https://sonar/component_measures?id=id&metric=uncovered_conditions&branch=master")

    async def test_duplicated_lines(self):
        """Test that the number of duplicated lines and the total number of lines are returned."""
        json = dict(
            component=dict(
                measures=[
                    dict(metric="duplicated_lines", value="10"), dict(metric="lines", value="100")]))
        metric = dict(type="duplicated_lines", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="10", total="100",
            landing_url="https://sonar/component_measures?id=id&metric=duplicated_lines&branch=master")

    async def test_many_parameters(self):
        """Test that the number of functions with too many parameters is returned."""
        self.sources["source_id"]["parameters"]["rules"] = ["rule1"]
        many_parameters_json = dict(total="2", issues=[])
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        metric = dict(type="many_parameters", addition="sum", sources=self.sources)
        response = await self.collect(
            metric,
            get_request_json_side_effect=[
                {}, many_parameters_json, functions_json, many_parameters_json, functions_json, many_parameters_json])
        self.assert_measurement(
            response, value="2", total="4",
            landing_url=f"{self.issues_landing_url}&rules=c:S107,csharpsquid:S107,csharpsquid:S2436,cpp:S107,flex:S107,"
                        "javascript:ExcessiveParameterList,objc:S107,php:S107,plsql:PlSql.FunctionAndProcedureExcessive"
                        "Parameters,python:S107,squid:S00107,tsql:S107,typescript:S107")

    async def test_long_units(self):
        """Test that the number of long units is returned."""
        self.sources["source_id"]["parameters"]["rules"] = ["rule1"]
        long_units_json = dict(total="2", issues=[])
        functions_json = dict(component=dict(measures=[dict(metric="functions", value="4")]))
        metric = dict(type="long_units", addition="sum", sources=self.sources)
        response = await self.collect(
            metric, get_request_json_side_effect=[
                {}, long_units_json, functions_json, long_units_json, functions_json, long_units_json])
        self.assert_measurement(
            response, value="2", total="4",
            landing_url=f"{self.issues_landing_url}&rules=abap:S104,c:FileLoc,cpp:FileLoc,csharpsquid:S104,"
                        "csharpsquid:S138,flex:S138,go:S104,go:S138,javascript:S104,javascript:S138,kotlin:S104,"
                        "kotlin:S138,objc:FileLoc,php:S104,php:S138,php:S2042,Pylint:R0915,python:S104,ruby:S104,"
                        "ruby:S138,scala:S104,scala:S138,squid:S00104,squid:S1188,squid:S138,squid:S2972,swift:S104,"
                        "typescript:S104,typescript:S138,vbnet:S104,vbnet:S138,Web:FileLengthCheck,"
                        "Web:LongJavaScriptCheck")

    async def test_source_up_to_dateness(self):
        """Test that the number of days since the last analysis is returned."""
        json = dict(analyses=[dict(date="2019-03-29T14:20:15+0100")])
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        timezone_info = timezone(timedelta(hours=1))
        expected_age = (datetime.now(timezone_info) - datetime(2019, 3, 29, 14, 20, 15, tzinfo=timezone_info)).days
        self.assert_measurement(
            response, value=str(expected_age), landing_url="https://sonar/project/activity?id=id&branch=master")

    async def test_suppressed_violations(self):
        """Test that the number of suppressed violations includes both suppressed issues as well as suppressed rules."""
        violations_json = dict(
            total="1", issues=[dict(key="a", message="a", component="a", severity="INFO", type="BUG")])
        wont_fix_json = dict(
            total="1",
            issues=[
                dict(key="b", message="b", component="b", severity="MAJOR", type="CODE_SMELL", resolution="WONTFIX")])
        total_violations_json = dict(total="4")
        metric = dict(type="suppressed_violations", addition="sum", sources=self.sources)
        response = await self.collect(
            metric, get_request_json_side_effect=[{}, violations_json, wont_fix_json, total_violations_json])
        expected_entities = [
            dict(component="a", key="a", message="a", severity="info", type="bug",
                 resolution="", url="https://sonar/project/issues?id=id&issues=a&open=a&branch=master"),
            dict(component="b", key="b", message="b", severity="major", type="code_smell",
                 resolution="won't fix", url="https://sonar/project/issues?id=id&issues=b&open=b&branch=master")]
        self.assert_measurement(
            response, value="2", total="4", entities=expected_entities,
            landing_url=f"{self.issues_landing_url}&rules=csharpsquid:S1309,php:NoSonar,Pylint:I0011,Pylint:I0020,"
                        "squid:NoSonar,squid:S1309,squid:S1310,squid:S1315")

    async def test_loc_returns_ncloc_by_default(self):
        """Test that the number of lines of non-comment code is returned."""
        json = dict(component=dict(measures=[dict(metric="ncloc", value="1234")]))
        metric = dict(type="loc", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="1234", total="100",
            landing_url="https://sonar/component_measures?id=id&metric=ncloc&branch=master")

    async def test_loc_all_lines(self):
        """Test that the number of lines of code is returned."""
        self.sources["source_id"]["parameters"]["lines_to_count"] = "all lines"
        json = dict(component=dict(measures=[dict(metric="lines", value="1234")]))
        metric = dict(type="loc", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value="1234", total="100",
            landing_url="https://sonar/component_measures?id=id&metric=lines&branch=master")

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        json = dict(component=dict(measures=[dict(metric="tests", value="123")]))
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="123", total="123", landing_url=self.tests_landing_url)

    async def test_nr_of_skipped_tests(self):
        """Test that the number of skipped tests is returned."""
        json = dict(
            component=dict(measures=[dict(metric="tests", value="123"), dict(metric="skipped_tests", value="4")]))
        self.sources["source_id"]["parameters"]["test_result"] = ["skipped"]
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="4", total="123", landing_url=self.tests_landing_url)

    async def test_nr_of_tests_without_tests(self):
        """Test that the collector throws an exception if there are no tests."""
        json = dict(component=dict(measures=[]))
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value=None, total=None, parse_error="KeyError", landing_url=self.tests_landing_url)

    async def test_nr_of_tests_with_faulty_component(self):
        """Test that the measurement fails if the component does not exist."""
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(
            metric, get_request_json_return_value=dict(errors=[dict(msg="No such component")]))
        self.assert_measurement(
            response, value=None, total=None, connection_error="No such component", landing_url=self.tests_landing_url)
