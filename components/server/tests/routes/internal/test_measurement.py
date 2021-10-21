"""Unit tests for the measurement routes."""

import unittest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

from routes.internal import post_measurement

from ...fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SOURCE_ID2, SUBJECT_ID, SUBJECT_ID2


@patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("model.source.iso_timestamp", new=Mock(return_value="2020-01-01"))
@patch("bottle.request")
class PostMeasurementTests(unittest.TestCase):
    """Unit tests for the post measurement route."""

    def setUp(self):
        """Override to setup a mock database fixture with some content."""
        self.database = Mock()
        self.report = dict(
            _id="id",
            report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID2: {},
                SUBJECT_ID: dict(
                    metrics={
                        METRIC_ID: dict(
                            name="name",
                            type="metric_type",
                            scale="count",
                            addition="sum",
                            direction="<",
                            target="0",
                            near_target="10",
                            debt_target=None,
                            accept_debt=False,
                            tags=[],
                            sources={SOURCE_ID: dict(type="junit"), SOURCE_ID2: dict(type="junit")},
                        )
                    }
                ),
            },
        )
        self.database.reports.find.return_value = [self.report]
        self.data_model = dict(
            _id="",
            metrics=dict(metric_type=dict(direction="<", scales=["count"])),
            sources=dict(junit=dict(entities={})),
        )
        self.database.datamodels.find_one.return_value = self.data_model

        def set_measurement_id(measurement):
            """Fake setting a measurement id on the inserted measurement."""
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        self.old_measurement = dict(
            _id="id",
            metric_uuid=METRIC_ID,
            count=dict(status="target_met"),
            sources=[self.source(value="0"), self.source(source_uuid=SOURCE_ID2)],
        )
        self.database.measurements.find_one.return_value = self.old_measurement
        self.posted_measurement = dict(metric_uuid=METRIC_ID, sources=[])

    @staticmethod
    def source(*, source_uuid=SOURCE_ID, value="1", entities=None, entity_user_data=None, connection_error=None):
        """Return a measurement source."""
        return dict(
            source_uuid=source_uuid,
            value=value,
            total=None,
            parse_error=None,
            connection_error=connection_error,
            entities=entities or [],
            entity_user_data=entity_user_data or {},
        )

    @staticmethod
    def measurement(*, metric_uuid=METRIC_ID, sources=None, start="2019-01-01", end="2019-01-01", **scales):
        """Return a measurement."""
        return dict(metric_uuid=metric_uuid, sources=sources or [], start=start, end=end, **scales)

    @staticmethod
    def scale_measurement(
        *, target="0", near_target="10", debt_target=None, direction="<", value=None, status=None, status_start=None
    ):
        """Return a count measurement."""
        measurement = dict(
            target=target,
            near_target=near_target,
            debt_target=debt_target,
            direction=direction,
            value=value,
            status=status,
        )
        if status_start:
            measurement["status_start"] = status_start
        return measurement

    def test_first_measurement(self, request):
        """Post the first measurement for a metric."""
        self.database.measurements.find_one.return_value = None
        sources = self.posted_measurement["sources"] = [self.source(), self.source(source_uuid=SOURCE_ID2)]
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(count=self.scale_measurement(value="2", status="near_target_met"), sources=sources)
        )

    def test_first_measurement_two_scales(self, request):
        """Post the first measurement for a metric with two scales."""
        self.database.measurements.find_one.return_value = None
        self.data_model["metrics"]["metric_type"]["scales"].append("percentage")
        sources = self.posted_measurement["sources"] = [self.source(), self.source(source_uuid=SOURCE_ID2)]
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=sources,
                count=self.scale_measurement(value="2", status="near_target_met"),
                percentage=dict(direction="<", value="1", status="target_not_met"),
            )
        )

    def test_first_measurement_version_number_scale(self, request):
        """Post the first measurement on the version number scale."""
        self.database.measurements.find_one.return_value = None
        self.data_model["metrics"]["metric_type"]["scales"] = ["version_number"]
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["scale"] = "version_number"
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["addition"] = "min"
        self.posted_measurement["sources"] = [self.source(value="1.1.3")]
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[self.source(value="1.1.3")],
                version_number=self.scale_measurement(value="1.1.3", status="near_target_met"),
            )
        )

    def test_unchanged_measurement(self, request):
        """Post an unchanged measurement for a metric."""
        self.posted_measurement["sources"] = self.old_measurement["sources"]
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.update_one.assert_called_once_with(
            filter={"_id": "id"}, update={"$set": {"end": "2019-01-01"}}
        )

    def test_changed_measurement_value(self, request):
        """Post a changed measurement for a metric."""
        self.posted_measurement["sources"].append(self.source())
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[self.source()],
                count=self.scale_measurement(value="1", status="near_target_met", status_start="2019-01-01"),
            )
        )

    @patch("server_utilities.functions.datetime", new=Mock(now=Mock(return_value=datetime(2021, 1, 1))))
    def test_changed_measurement_entities(self, request):
        """Post a measurement whose value is the same, but with different entities.

        Entity user data will be changed as follows:
        - Entity data belonging to entities still present is simply copied.
        - Entity data no longer belonging to an entity because the entity disappeared will be marked as orphaned.
        - Entity data that was orphaned recently will still be orphaned.
        - Entity data that was orphaned long ago will be deleted.
        - Entity data that was orphaned, but whose entity reappears, will no longer be orphaned.
        """
        self.old_measurement["count"] = dict(status="near_target_met", status_start="2018-01-01", value="1")
        self.old_measurement["sources"] = [
            self.source(
                entities=[dict(key="a")],
                entity_user_data=dict(
                    a=dict(status="confirmed"),  # Will be newly orphaned
                    b=dict(status="confirmed", orphaned_since="2021-01-01"),  # Will be reunited with its entity
                    c=dict(status="confirmed", orphaned_since="2021-01-01"),  # Will still be orphaned
                    d=dict(status="confirmed", orphaned_since="2020-01-01"),  # Orphaned too long, will be deleted
                ),
            )
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="b")]))
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[
                    self.source(
                        entities=[dict(key="b")],
                        entity_user_data=dict(
                            a=dict(status="confirmed", orphaned_since="2020-01-01"),  # Newly orphaned
                            b=dict(status="confirmed"),  # No longer orphaned
                            c=dict(status="confirmed", orphaned_since="2021-01-01"),  # Still orphaned
                        ),
                    )
                ],
                count=self.scale_measurement(value="1", status="near_target_met", status_start="2018-01-01"),
            )
        )

    def test_changed_measurement_entity_key(self, request):
        """Post a measurement whose value and entities are the same, except for a changed entity key."""
        self.old_measurement["sources"] = [
            self.source(entities=[dict(key="a")], entity_user_data=dict(a=dict(status="confirmed")))
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(old_key="a", key="b")]))
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[
                    self.source(
                        entities=[dict(key="b", old_key="a")], entity_user_data=dict(b=dict(status="confirmed"))
                    )
                ],
                count=self.scale_measurement(value="1", status="near_target_met", status_start="2019-01-01"),
            )
        )

    def test_ignored_measurement_entities(self, request):
        """Post a measurement where the old one has ignored entities."""
        self.old_measurement["sources"] = [
            self.source(
                entities=[dict(key="entity1")],
                entity_user_data=dict(entity1=dict(status="false_positive", rationale="Rationale")),
            )
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="entity1")]))
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.update_one.assert_called_once_with(
            filter={"_id": "id"}, update={"$set": {"end": "2019-01-01"}}
        )

    def test_ignored_measurement_entities_and_failed_measurement(self, request):
        """Post a measurement where the last successful one has ignored entities."""
        self.database.measurements.find_one.side_effect = [
            dict(
                _id="id1",
                count=dict(status=None, status_start="2018-12-01"),
                sources=[self.source()],
            ),
            dict(
                _id="id2",
                status="target_met",
                sources=[
                    self.source(
                        entities=[dict(key="entity1")],
                        entity_user_data=dict(entity1=dict(status="false_positive", rationale="Rationale")),
                    )
                ],
            ),
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="entity1")]))
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[
                    self.source(
                        entities=[{"key": "entity1"}],
                        entity_user_data={"entity1": {"status": "false_positive", "rationale": "Rationale"}},
                    )
                ],
                count=self.scale_measurement(value="0", status="target_met", status_start="2019-01-01"),
            )
        )

    def test_all_previous_measurements_were_failed_measurements(self, request):
        """Post a measurement without a last successful one."""
        self.database.measurements.find_one.side_effect = [
            dict(_id="id1", count=dict(status=None), sources=[self.source(connection_error="Error")]),
            None,
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="entity1")]))
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[self.source(entities=[{"key": "entity1"}], entity_user_data={})],
                count=self.scale_measurement(value="1", status="near_target_met", status_start="2019-01-01"),
            )
        )

    def test_deleted_metric(self, request):
        """Post a measurement for a deleted metric."""
        self.report["subjects"][SUBJECT_ID]["metrics"] = {}
        self.posted_measurement["sources"] = self.old_measurement["sources"]
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.update_one.assert_not_called()
        self.database.measurements.insert_one.assert_not_called()

    def test_deleted_source(self, request):
        """Post a measurement for a deleted source."""
        del self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID2]
        self.posted_measurement["sources"] = self.old_measurement["sources"]
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.update_one.assert_not_called()
        self.database.measurements.insert_one.assert_not_called()

    def test_new_source(self, request):
        """Post a measurement for a new source."""
        del self.old_measurement["sources"][0]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="entity1")]))
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[self.source(entities=[{"key": "entity1"}], entity_user_data={})],
                count=self.scale_measurement(value="1", status="near_target_met", status_start="2019-01-01"),
            )
        )

    def test_accepted_technical_debt(self, request):
        """Test that a new measurement is not added when technical debt has not expired yet."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"] = True
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        self.old_measurement["count"] = self.scale_measurement(
            value="1", status="debt_target_met", debt_target="100", status_start="once upon a time"
        )
        self.posted_measurement["sources"].append(self.source())
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[self.source()],
                count=self.scale_measurement(
                    debt_target="100", value="1", status="debt_target_met", status_start="once upon a time"
                ),
            )
        )

    def test_expired_technical_debt(self, request):
        """Test that a new measurement is added when technical debt expires."""
        debt_end_date = date.today() - timedelta(days=1)
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"] = debt_end_date.isoformat()
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        self.posted_measurement["sources"].append(self.source())
        self.old_measurement["count"] = self.scale_measurement(value="1", status="debt_target_met", debt_target="100")
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[self.source()],
                count=self.scale_measurement(value="1", status="near_target_met", status_start="2019-01-01"),
            )
        )

    def test_technical_debt_off(self, request):
        """Test that a new measurement is added when technical debt has been turned off."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"] = False
        self.posted_measurement["sources"].append(self.source())
        self.old_measurement["count"] = self.scale_measurement(value="1", status="debt_target_met", debt_target="100")
        request.json = self.posted_measurement
        post_measurement(self.database)
        self.database.measurements.insert_one.assert_called_once_with(
            self.measurement(
                sources=[self.source()],
                count=self.scale_measurement(value="1", status="near_target_met", status_start="2019-01-01"),
            )
        )
