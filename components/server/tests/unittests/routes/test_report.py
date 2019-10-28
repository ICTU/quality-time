"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock, patch, MagicMock

import requests

from routes.report import (
    delete_metric, delete_report, delete_source, delete_subject, get_metrics, get_reports,
    get_tag_report, post_metric_attribute, post_metric_new, post_new_subject, post_report_attribute, post_report_new,
    post_reports_attribute, post_source_attribute, post_source_new, post_source_parameter, post_subject_attribute
)
from utilities.functions import iso_timestamp


@patch("bottle.request")
class PostReportAttributeTest(unittest.TestCase):
    """Unit tests for the post report attribute route."""
    def test_post_report_name(self, request):
        """Test that the report name can be changed."""
        report = dict(_id="id", report_uuid="report_uuid")
        request.json = dict(name="name")
        database = Mock()
        database.reports.find_one.return_value = report
        database.sessions.find_one.return_value = dict(user="John")
        database.datamodels.find_one.return_value = dict()
        self.assertEqual(dict(ok=True), post_report_attribute("report_uuid", "name", database))
        database.reports.insert.assert_called_once_with(report)
        self.assertEqual(
            dict(description="John changed the name of report '' from '' to 'name'.", report_uuid="report_uuid"),
            report["delta"])


@patch("bottle.request")
class PostSubjectAttributeTest(unittest.TestCase):
    """Unit tests for the post subject report attribute route."""

    def setUp(self):
        self.database = Mock()
        self.report = dict(
            _id="id", report_uuid="report_uuid", title="Report",
            subjects=dict(subject_uuid=dict(name="subject1"), subject_uuid2=dict(name="subject2")))
        self.database.reports.find_one.return_value = self.report
        self.database.datamodels.find_one.return_value = dict()
        self.database.sessions.find_one.return_value = dict(user="John")

    def test_post_subject_name(self, request):
        """Test that the subject name can be changed."""
        request.json = dict(name="new name")
        self.assertEqual(dict(ok=True), post_subject_attribute("report_uuid", "subject_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(
                description="John changed the name of subject 'subject1' in report 'Report' from 'subject1' to "
                            "'new name'.",
                report_uuid="report_uuid", subject_uuid="subject_uuid"),
            self.report["delta"])

    def test_post_position_first(self, request):
        """Test that a subject can be moved to the top."""
        request.json = dict(position="first")
        self.assertEqual(
            dict(ok=True), post_subject_attribute("report_uuid", "subject_uuid2", "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(["subject_uuid2", "subject_uuid"], list(self.report["subjects"].keys()))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid2",
                 description="John changed the position of subject 'subject2' in report 'Report' from '1' to '0'."),
            self.report["delta"])

    def test_post_position_last(self, request):
        """Test that a subject can be moved to the bottom."""
        request.json = dict(position="last")
        self.assertEqual(
            dict(ok=True), post_subject_attribute("report_uuid", "subject_uuid", "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(["subject_uuid2", "subject_uuid"], list(self.report["subjects"].keys()))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid",
                 description="John changed the position of subject 'subject1' in report 'Report' from '0' to '1'."),
            self.report["delta"])

    def test_post_position_previous(self, request):
        """Test that a subject can be moved up."""
        request.json = dict(position="previous")
        self.assertEqual(
            dict(ok=True), post_subject_attribute("report_uuid", "subject_uuid2", "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(["subject_uuid2", "subject_uuid"], list(self.report["subjects"].keys()))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid2",
                 description="John changed the position of subject 'subject2' in report 'Report' from '1' to '0'."),
            self.report["delta"])

    def test_post_position_next(self, request):
        """Test that a subject can be moved down."""
        request.json = dict(position="next")
        self.assertEqual(
            dict(ok=True), post_subject_attribute("report_uuid", "subject_uuid", "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(["subject_uuid2", "subject_uuid"], list(self.report["subjects"].keys()))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid",
                 description="John changed the position of subject 'subject1' in report 'Report' from '0' to '1'."),
            self.report["delta"])

    def test_post_position_first_previous(self, request):
        """Test that moving the first subject up does nothing."""
        request.json = dict(position="previous")
        self.assertEqual(
            dict(ok=True), post_subject_attribute("report_uuid", "subject_uuid", "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual(["subject_uuid", "subject_uuid2"], list(self.report["subjects"].keys()))

    def test_post_position_last_next(self, request):
        """Test that moving the last subject down does nothing."""
        request.json = dict(position="next")
        self.assertEqual(
            dict(ok=True), post_subject_attribute("report_uuid", "subject_uuid2", "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual(["subject_uuid", "subject_uuid2"], list(self.report["subjects"].keys()))


@patch("database.reports.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("bottle.request")
class PostMetricAttributeTest(unittest.TestCase):
    """Unit tests for the post metric attribute route."""

    def setUp(self):
        self.report = dict(
            _id="id", report_uuid="report_uuid", title="Report",
            subjects=dict(
                other_subject=dict(metrics=dict()),
                subject_uuid=dict(
                    name='Subject',
                    metrics=dict(
                        metric_uuid=dict(
                            name="name", type="old_type", scale="count", addition="sum", direction="<", target="0",
                            near_target="10", debt_target=None, accept_debt=False, tags=[],
                            sources=dict(source_uuid=dict())),
                        metric_uuid2=dict(name="name2")))))
        self.database = Mock()
        self.database.reports.find_one.return_value = self.report
        self.database.sessions.find_one.return_value = dict(user="John")
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            metrics=dict(
                old_type=dict(name="Old type", scales=["count"]),
                new_type=dict(
                    scales=["count"], default_scale="count", addition="sum", direction="<", target="0", near_target="1",
                    tags=[], sources=["source_type"])))

    def test_post_metric_name(self, request):
        """Test that the metric name can be changed."""
        request.json = dict(name="ABC")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="John changed the name of metric 'name' of subject 'Subject' in report 'Report' "
                             "from 'name' to 'ABC'."),
            self.report["delta"])

    def test_post_metric_type(self, request):
        """Test that the metric type can be changed."""
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="John changed the type of metric 'name' of subject 'Subject' in report 'Report' "
                             "from 'old_type' to 'new_type'."),
            self.report["delta"])

    def test_post_metric_target_without_measurements(self, request):
        """Test that changing the metric target doesnt't add a new measurement if none exist."""
        self.database.measurements.find_one.return_value = None
        request.json = dict(target="10")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "target", self.database))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="John changed the target of metric 'name' of subject 'Subject' in report 'Report' "
                             "from '0' to '10'."),
            self.report["delta"])

    @patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_target_with_measurements(self, request):
        """Test that changing the metric target adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid="metric_uuid", sources=[])

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        request.json = dict(target="10")
        self.assertEqual(
            dict(
                _id="measurement_id", end="2019-01-01", sources=[], start="2019-01-01",
                count=dict(status=None, value=None), metric_uuid="metric_uuid", last=True),
            post_metric_attribute("report_uuid", "metric_uuid", "target", self.database))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="John changed the target of metric 'name' of subject 'Subject' in report 'Report' "
                             "from '0' to '10'."),
            self.report["delta"])

    @patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_debt_end_date_with_measurements(self, request):
        """Test that changing the metric debt end date adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid="metric_uuid", sources=[])

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        request.json = dict(debt_end_date="2019-06-07")
        self.assertEqual(
            dict(
                _id="measurement_id", end="2019-01-01", sources=[], start="2019-01-01", last=True,
                metric_uuid="metric_uuid", count=dict(value=None, status=None)),
            post_metric_attribute("report_uuid", "metric_uuid", "debt_end_date", self.database))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="John changed the debt_end_date of metric 'name' of subject 'Subject' in report "
                             "'Report' from '' to '2019-06-07'."),
            self.report["delta"])

    def test_post_unsafe_comment(self, request):
        """Test that comments are sanitized, since they are displayed as inner HTML in the frontend."""
        request.json = dict(comment='Comment with script<script type="text/javascript">alert("Danger")</script>')
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "comment", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="John changed the comment of metric 'name' of subject 'Subject' in report 'Report' "
                             "from '' to 'Comment with script'."),
            self.report["delta"])

    def test_post_comment_with_link(self, request):
        """Test that urls in comments are transformed into anchors."""
        request.json = dict(comment='Comment with url https://google.com')
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "comment", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="""John changed the comment of metric 'name' of subject 'Subject' in report 'Report' \
from '' to '<p>Comment with url <a href="https://google.com">https://google.com</a></p>'."""),
            self.report["delta"])

    def test_post_position_first(self, request):
        """Test that a metric can be moved to the top of the list."""
        request.json = dict(position="first")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid2", "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            ["metric_uuid2", "metric_uuid"], list(self.report["subjects"]["subject_uuid"]["metrics"].keys()))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid2",
                 description="John changed the position of metric 'name2' of subject 'Subject' in report "
                             "'Report' from '1' to '0'."),
            self.report["delta"])

    def test_post_position_last(self, request):
        """Test that a metric can be moved to the bottom of the list."""
        request.json = dict(position="last")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            ["metric_uuid2", "metric_uuid"], list(self.report["subjects"]["subject_uuid"]["metrics"].keys()))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="John changed the position of metric 'name' of subject 'Subject' in report "
                             "'Report' from '0' to '1'."),
            self.report["delta"])

    def test_post_position_previous(self, request):
        """Test that a metric can be moved up."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid2", "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            ["metric_uuid2", "metric_uuid"], list(self.report["subjects"]["subject_uuid"]["metrics"].keys()))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid2",
                 description="John changed the position of metric 'name2' of subject 'Subject' in report "
                             "'Report' from '1' to '0'."),
            self.report["delta"])

    def test_post_position_next(self, request):
        """Test that a metric can be moved down."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            ["metric_uuid2", "metric_uuid"], list(self.report["subjects"]["subject_uuid"]["metrics"].keys()))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="John changed the position of metric 'name' of subject 'Subject' in report "
                             "'Report' from '0' to '1'."),
            self.report["delta"])

    def test_post_position_first_previous(self, request):
        """Test that moving the first metric up does nothing."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual(
            ["metric_uuid", "metric_uuid2"], list(self.report["subjects"]["subject_uuid"]["metrics"].keys()))

    def test_post_position_last_next(self, request):
        """Test that moving the last metric down does nothing."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid2", "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual(
            ["metric_uuid", "metric_uuid2"], list(self.report["subjects"]["subject_uuid"]["metrics"].keys()))


@patch("bottle.request")
class PostSourceAttributeTest(unittest.TestCase):
    """Unit tests for the post source attribute route."""

    def setUp(self):
        self.report = dict(
            _id="report_uuid", title="Report",
            subjects=dict(
                subject_uuid=dict(
                    name="Subject",
                    metrics=dict(
                        metric_uuid=dict(
                            name="Metric", type="type", sources=dict(source_uuid=dict(name="Source", type="type")))))))
        self.database = Mock()
        self.database.reports.find_one.return_value = self.report
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="id", sources=dict(type=dict(name="Type"), new_type=dict(parameters=dict())))

    def test_name(self, request):
        """Test that the source name can be changed."""
        request.json = dict(name="New source name")
        self.assertEqual(dict(ok=True), post_source_attribute("report_uuid", "source_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 source_uuid="source_uuid",
                 description="Jenny changed the name of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from 'Source' to 'New source name'."),
            self.report["delta"])

    def test_post_source_type(self, request):
        """Test that the source type can be changed."""
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_source_attribute("report_uuid", "source_uuid", "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 source_uuid="source_uuid",
                 description="Jenny changed the type of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from 'type' to 'new_type'."),
            self.report["delta"])


@patch("bottle.request")
class PostSourceParameterTest(unittest.TestCase):
    """Unit tests for the post source parameter route."""

    def setUp(self):
        self.report = dict(
            _id="report_uuid", title="Report",
            subjects=dict(
                subject_uuid=dict(
                    name="Subject",
                    metrics=dict(
                        metric_uuid=dict(
                            name="Metric", type="type",
                            sources=dict(source_uuid=dict(name="Source", type="type", parameters=dict())))))))
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.reports.find_one.return_value = self.report
        self.database.datamodels.find_one.return_value = dict(
            _id="id", sources=dict(type=dict(parameters=dict(url=dict(type="url"), password=dict(type="password")))))

    @patch.object(requests, 'get')
    def test_url(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = MagicMock(status_code=123, reason='A good reason')
        request.json = dict(url="https://url")
        response = post_source_parameter("report_uuid", "source_uuid", "url", self.database)
        self.assertTrue(response['ok'])
        self.assertEqual(response['availability'], [{"status_code": 123, "reason": 'A good reason',
                                                     'source_uuid': 'source_uuid', "parameter_key": 'url'}])
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_called_once_with('https://url', auth=None)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 source_uuid="source_uuid",
                 description="Jenny changed the url of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from '' to 'https://url'."),
            self.report["delta"])

    @patch.object(requests, 'get')
    def test_url_http_error(self, mock_get, request):
        """Test that the error is reported if a request exception occurs, while checking connection of a url."""
        mock_get.side_effect = requests.exceptions.RequestException
        request.json = dict(url="https://url")
        response = post_source_parameter("report_uuid", "source_uuid", "url", self.database)
        self.assertTrue(response['ok'])
        self.assertEqual(response['availability'], [{"status_code": -1, "reason": 'Unknown error',
                                                     'source_uuid': 'source_uuid', "parameter_key": 'url'}])
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 source_uuid="source_uuid",
                 description="Jenny changed the url of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from '' to 'https://url'."),
            self.report["delta"])

    @patch.object(requests, 'get')
    def test_url_with_user(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        database = self.database
        database.datamodels.find_one.return_value = dict(_id="id", sources=dict(type=dict(parameters=dict(url=dict(
            type="url"), username=dict(type="string"), password=dict(type="pwd")))))
        srcs = database.reports.find_one.return_value['subjects']['subject_uuid']['metrics']['metric_uuid']['sources']
        srcs['source_uuid']['parameters']['username'] = 'un'
        srcs['source_uuid']['parameters']['password'] = 'pwd'
        mock_get.return_value = MagicMock(status_code=123, reason='A good reason')
        request.json = dict(url="https://url")
        response = post_source_parameter("report_uuid", "source_uuid", "url", database)
        self.assertTrue(response['ok'])
        self.assertEqual(response['availability'], [{"status_code": 123, "reason": 'A good reason',
                                                     'source_uuid': 'source_uuid', "parameter_key": 'url'}])
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_called_once_with('https://url', auth=('un', 'pwd'))

    @patch.object(requests, 'get')
    def test_url_no_url_type(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        database = self.database
        database.datamodels.find_one.return_value = dict(_id="id", sources=dict(type=dict(parameters=dict(url=dict(
            type="string"), username=dict(type="string"), password=dict(type="pwd")))))
        mock_get.return_value = MagicMock(status_code=123, reason='A good reason')
        request.json = dict(url="unimportant")
        response = post_source_parameter("report_uuid", "source_uuid", "url", database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_not_called()

    @patch.object(requests, 'get')
    def test_url_with_token(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        database = self.database
        database.datamodels.find_one.return_value = dict(_id="id", sources=dict(type=dict(parameters=dict(url=dict(
            type="url"), username=dict(type="string"), private_token=dict(type="pwd")))))
        mock_get.return_value = MagicMock(status_code=123, reason='A good reason')
        request.json = dict(url="https://url")
        srcs = database.reports.find_one.return_value['subjects']['subject_uuid']['metrics']['metric_uuid']['sources']
        srcs['source_uuid']['parameters']['private_token'] = 'xxx'
        response = post_source_parameter("report_uuid", "source_uuid", "url", database)
        self.assertTrue(response['ok'])
        self.assertEqual(response['availability'], [{"status_code": 123, "reason": 'A good reason',
                                                     'source_uuid': 'source_uuid', "parameter_key": 'url'}])
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_called_once_with('https://url', auth=('xxx', ''))

    @patch.object(requests, 'get')
    def test_urls_connection_on_update_other_field(self, mock_get, request):
        """Test that the all urls availability is checked when a parameter is changed."""
        database = self.database
        database.datamodels.find_one.return_value = dict(
            _id="id", sources=dict(type=dict(parameters=dict(
                url=dict(type="url", validate_on='password'), landing_url=dict(type="url"),
                password=dict(type="password")))))
        mock_get.side_effect = [MagicMock(status_code=123, reason='A good reason')]
        request.json = dict(password="changed")
        srcs = database.reports.find_one.return_value['subjects']['subject_uuid']['metrics']['metric_uuid']['sources']
        srcs['source_uuid']['parameters']['url'] = "https://url"
        response = post_source_parameter("report_uuid", "source_uuid", "password", database)
        self.assertTrue(response['ok'])
        self.assertEqual(response['availability'], [{"status_code": 123, "reason": 'A good reason',
                                                     'source_uuid': 'source_uuid', "parameter_key": 'url'}])
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_password(self, request):
        """Test that the password can be changed and is not logged."""
        request.json = dict(url="unimportant", password="secret")
        response = post_source_parameter("report_uuid", "source_uuid", "password", self.database)
        self.assertTrue(response['ok'])
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 source_uuid="source_uuid",
                 description="Jenny changed the password of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from '' to '******'."),
            self.report["delta"])


class SourceTest(unittest.TestCase):
    """Unit tests for adding and deleting sources."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(metric_type=dict(name="Metric Type", direction="<", default_source="source_type")),
            sources=dict(source_type=dict(parameters=dict())))

    def test_add_source(self):
        """Test that a new source is added."""
        report = dict(
            _id="report_uuid", title="Report",
            subjects=dict(
                subject_uuid=dict(
                    name="Subject",
                    metrics=dict(
                        metric_uuid=dict(
                            name=None, type="metric_type", addition="sum", target="0", near_target="10",
                            debt_target=None, accept_debt=False, tags=[], sources=dict())))))
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), post_source_new("report_uuid", "metric_uuid", self.database))
        self.database.reports.insert.assert_called_once_with(report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="Jenny added a new source to metric 'Metric Type' of subject 'Subject' in report "
                             "'Report'."),
            report["delta"])

    def test_delete_source(self):
        """Test that the source can be deleted."""
        report = dict(
            _id="report_uuid", title="Report",
            subjects=dict(
                subject_uuid=dict(
                    name="Subject",
                    metrics=dict(
                        metric_uuid=dict(
                            type="type", name="Metric", sources=dict(source_uuid=dict(name="Source")))))))
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), delete_source("report_uuid", "source_uuid", self.database))
        self.database.reports.insert.assert_called_once_with(report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid", metric_uuid="metric_uuid",
                 description="Jenny deleted the source 'Source' from metric 'Metric' of subject 'Subject' in report "
                             "'Report'."),
            report["delta"])


class MetricTest(unittest.TestCase):
    """Unit tests for adding and deleting metrics."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(
                metric_type=dict(
                    default_scale="count", addition="sum", direction="<", target="0", near_target="1", tags=[])))

    def test_add_metric(self):
        """Test that a metric can be added."""
        report = dict(
            _id="report_uuid", title="Report", subjects=dict(subject_uuid=dict(name="Subject", metrics=dict())))
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), post_metric_new("report_uuid", "subject_uuid", self.database))
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid",
                 description="Jenny added a new metric to subject 'Subject' in report 'Report'."),
            report["delta"])

    def test_get_metrics(self):
        """Test that the metrics can be retrieved and deleted reports are skipped."""
        report = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict(type="metric_type", tags=[])))))
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.reports.distinct.return_value = ["report_uuid", "deleted_report"]
        self.database.reports.find_one.side_effect = [report, dict(deleted=True)]
        self.database.measurements.find.return_value = [dict(
            _id="id", metric_uuid="metric_uuid", status="red",
            sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")])]
        self.assertEqual(dict(metric_uuid=dict(type="metric_type", tags=[])), get_metrics(self.database))

    def test_delete_metric(self):
        """Test that the metric can be deleted."""
        report = dict(
            _id="report_uuid", title="Report",
            subjects=dict(subject_uuid=dict(name="Subject", metrics=dict(metric_uuid=dict(name="Metric")))))
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), delete_metric("report_uuid", "metric_uuid", self.database))
        self.database.reports.insert.assert_called_once_with(report)
        self.assertEqual(
            dict(report_uuid="report_uuid", subject_uuid="subject_uuid",
                 description=f"Jenny deleted metric 'Metric' from subject 'Subject' in report 'Report'."),
            report["delta"])


class SubjectTest(unittest.TestCase):
    """Unit tests for adding and deleting subjects."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.report = dict(title="Report", subjects=dict(subject_uuid=dict(name="ABC")))
        self.database.reports.find_one.return_value = self.report
        self.database.datamodels.find_one.return_value = dict()

    def test_add_subject(self):
        """Test that a subject can be added."""
        self.database.datamodels.find_one.return_value = dict(
            _id="", subjects=dict(subject_type=dict(name="Subject", description="")))
        self.assertEqual(dict(ok=True), post_new_subject("report_uuid", self.database))
        self.assertEqual(
            dict(report_uuid="report_uuid", description="Jenny created a new subject in report 'Report'."),
            self.report["delta"])

    def test_delete_subject(self):
        """Test that a subject can be deleted."""
        self.assertEqual(dict(ok=True), delete_subject("report_uuid", "subject_uuid", self.database))
        self.assertEqual(
            dict(report_uuid="report_uuid", description="Jenny deleted the subject 'ABC' from report 'Report'."),
            self.report["delta"])


class ReportTest(unittest.TestCase):
    """Unit tests for adding, deleting, and getting reports."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")

    def test_add_report(self):
        """Test that a report can be added."""
        self.assertEqual(dict(ok=True), post_report_new(self.database))
        self.database.reports.insert.assert_called_once()
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual("New report", inserted["title"])
        self.assertEqual("Jenny created this report.", inserted["delta"]["description"])

    def test_get_report(self):
        """Test that a report can be retrieved."""
        self.database.datamodels.find_one.return_value = dict(
            _id="id", metrics=dict(metric_type=dict(default_scale="count")))
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.measurements.find.return_value = [
            dict(
                _id="id", metric_uuid="metric_uuid", status="red",
                sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")])]
        self.database.reports.distinct.return_value = ["report_uuid"]
        report = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            type="metric_type", addition="sum", target="0", near_target="10", debt_target="0",
                            accept_debt=False, tags=["a"])))))
        self.database.reports.find_one.return_value = report
        report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=1)
        report["summary_by_subject"] = dict(subject_uuid=dict(red=0, green=0, yellow=0, grey=0, white=1))
        report["summary_by_tag"] = {}
        self.assertEqual(dict(_id="id", title="Reports", subtitle="", reports=[report]), get_reports(self.database))

    def test_delete_report(self):
        """Test that the report can be deleted."""
        report = dict(_id="1", report_uuid="report_uuid", title="Report")
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), delete_report("report_uuid", self.database))

    @patch("bottle.request")
    def test_post_reports_attribute(self, request):
        """Test that a reports (overview) attribute can be changed."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports")
        request.json = dict(title="All the reports")
        self.assertEqual(dict(ok=True), post_reports_attribute("title", self.database))

    @patch("bottle.request")
    def test_get_tag_report(self, request):
        """Test that a tag report can be retrieved."""
        date_time = request.report_date = iso_timestamp()
        self.database.datamodels.find_one.return_value = dict(
            _id="id", metrics=dict(metric_type=dict(default_scale="count")))
        self.database.reports.find_one.return_value = None
        self.database.measurements.find.return_value = []
        self.database.reports.distinct.return_value = ["report_uuid"]
        self.database.reports.find_one.return_value = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(
                subject_without_metrics=dict(metrics=dict()),
                subject_uuid=dict(
                    metrics=dict(
                        metric_with_tag=dict(type="metric_type", tags=["tag"]),
                        metric_without_tag=dict(type="metric_type", tags=["other tag"])))))
        self.assertEqual(
            dict(
                summary=dict(red=0, green=0, yellow=0, grey=0, white=1),
                summary_by_tag=dict(tag=dict(red=0, green=0, yellow=0, grey=0, white=1)),
                summary_by_subject=dict(subject_uuid=dict(red=0, green=0, yellow=0, grey=0, white=1)),
                title='Report for tag "tag"', subtitle="Note: tag reports are read-only", report_uuid="tag-tag",
                timestamp=date_time, subjects=dict(
                    subject_uuid=dict(metrics=dict(metric_with_tag=dict(type="metric_type", tags=["tag"]))))),
            get_tag_report("tag", self.database))
