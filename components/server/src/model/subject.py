from model.measurement import Measurement
from model.metric import Metric
from server_utilities.type import ReportId, SubjectId


class Subject(dict):
    """Class representing a report."""

    def __init__(self, data_model, subject_data: dict, subject_uuid: SubjectId, report_uuid: ReportId) -> None:
        """Instantiate a Subject."""
        self.__data_model = data_model
        self.uuid = subject_uuid
        self.report_uuid = report_uuid

        metric_data = subject_data.pop("metrics")
        self.metrics_dict = self._instantiate_metrics(metric_data)
        self.metrics = list(self.metrics_dict.values())
        self.metric_uuids = list(self.metrics_dict.keys())

        super().__init__(subject_data)

    def __eq__(self, other):
        """Return whether the metrics are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

    def _instantiate_metrics(self, metric_data: dict) -> dict[str, Metric]:
        """Create metrics from metric_data."""
        metrics = {}
        for metric_uuid, metric_dict in metric_data.items():
            metrics[metric_uuid] = Metric(self.__data_model, metric_dict, metric_uuid, self.uuid)
        return metrics

    def summarize(self, measurements: dict[str, Measurement] | None):
        """Create a summary dict of this subject."""
        summary = dict(self)
        summary["metrics"] = {}
        for metric in self.metrics:
            metric_measurements = measurements[metric.uuid] if metric.uuid in measurements else None
            summary["metrics"][metric.uuid] = metric.summarize(metric_measurements)
        return summary
