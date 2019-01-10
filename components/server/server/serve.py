"""Quality-time server."""

from gevent import monkey
monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import datetime
import json
import logging
import os
import time

import dataset
import bottle
from sqlalchemy.pool import NullPool


DATABASE = None


def measurement_key(measurement) -> str:
    """Create a database key from the measurement."""
    request = measurement["request"]
    return json.dumps(dict(metric=request["metric"], source=request["source"],
                           urls=request["urls"], components=request["components"]))


@bottle.get("/report")
def get_report():
    """Return the quality report."""
    logging.info(bottle.request)
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    report = dict(subjects=[])
    for subject_row in DATABASE["subjects"].all():
        subject = dict(title=subject_row["title"], metrics=[])
        for metric_row in DATABASE["metrics"].find(subject=subject_row["id"]):
            subject["metrics"].append(metric_row["url"])
        report["subjects"].append(subject)
    return report


@bottle.post("/measurement")
def post_measurement() -> None:
    """Put the measurement in the database."""
    def equal_measurements(measure1, measure2):
        """Return whether the measurements have equal values and targets."""
        return measure1["measurement"] == measure2["measurement"] and measure1["target"] == measure2["target"] and \
            measure1["status"] == measure2["status"] and measure1["calculation_error"] == measure2["calculation_error"]

    logging.info(bottle.request)
    measurement = bottle.request.json
    timestamp_string = measurement["measurement"]["timestamp"]
    key = measurement_key(measurement)
    table = DATABASE["measurements"]
    latest_measurement_row = table.find_one(key=key, order_by="-timestamp")
    if latest_measurement_row:
        latest_measurement = json.loads(latest_measurement_row["measurement"])
        if equal_measurements(latest_measurement["measurement"], measurement["measurement"]):
            latest_measurement["measurement"]["end"] = timestamp_string
            table.update(dict(id=latest_measurement_row["id"], measurement=json.dumps(latest_measurement)), ["id"])
            return
    measurement["measurement"]["start"] = timestamp_string
    measurement["measurement"]["end"] = timestamp_string
    timestamp = datetime.datetime.fromisoformat(timestamp_string)
    table.insert(dict(timestamp=timestamp, key=key, measurement=json.dumps(measurement)))


@bottle.get("/comment/<metric_name>/<source_name>")
def get_comment(metric_name: str, source_name: str):
    """Return the comment for the metric."""
    logging.info(bottle.request)
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    urls = bottle.request.query.getall("url")  # pylint: disable=no-member
    components = bottle.request.query.getall("component")  # pylint: disable=no-member
    key = json.dumps(dict(metric=metric_name, source=source_name, urls=urls, components=components))
    comment_row = DATABASE["comments"].find_one(metric=key)
    comment = comment_row.get("comment", "") if comment_row else ""
    return dict(comment=comment)


@bottle.route("/comment/<metric_name>/<source_name>", method="OPTIONS")
def comment_options(metric_name: str, source_name: str) -> str:
    """Return the options for the comment POST."""
    logging.info(bottle.request)
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    bottle.response.set_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    bottle.response.headers["Access-Control-Allow-Headers"] = \
        "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
    return ""


@bottle.post("/comment/<metric_name>/<source_name>")
def post_comment(metric_name: str, source_name: str):
    """Save the comment for the metric."""
    logging.info(bottle.request)
    comment = bottle.request.json
    urls = bottle.request.query.getall("url")  # pylint: disable=no-member
    components = bottle.request.query.getall("component")  # pylint: disable=no-member
    key = json.dumps(dict(metric=metric_name, source=source_name, urls=urls, components=components))
    comment_row = dict(metric=key, comment=comment.get("comment", ""))
    DATABASE["comments"].upsert(comment_row, ["metric"])


@bottle.route("/nr_measurements", method="OPTIONS")
def options() -> str:
    """Return the options for the number of measurements server sent events stream."""
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    bottle.response.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    bottle.response.set_header("Access-Control-Allow-Headers", "X-REQUESTED-WITH, CACHE-CONTROL, LAST-EVENT-ID")
    bottle.response.set_header("Content-Type", "text/plain")
    return ""


def sse_pack(event_id: str, event: str, data: str, retry: str = "2000") -> str:
    """Pack data in Server-Sent Events (SSE) format"""
    return f"retry: {retry}\nid: {event_id}\nevent: {event}\ndata: {data}\n\n"


@bottle.get("/nr_measurements")
def stream_nr_measurements():
    """Return the number of measurements as server sent events."""
    # Keep event IDs consistent
    event_id = int(bottle.request.get_header("Last-Event-Id", -1)) + 1

    # Set the response headers
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    bottle.response.set_header("Content-Type", "text/event-stream")

    # Provide an initial data dump to each new client and set up our
    # message payload with a retry value in case of connection failure
    data = len(DATABASE["measurements"])
    yield sse_pack(event_id, "init", data)

    # Now give the client updates as they arrive
    while True:
        time.sleep(10)
        new_data = len(DATABASE["measurements"])
        if new_data > data:
            data = new_data
            event_id += 1
            yield sse_pack(event_id, "delta", data)


@bottle.get("/<metric_name>/<source_name>")
def get_measurements(metric_name: str, source_name: str):
    """Return the measurements for the metric/source."""
    logging.info(bottle.request)
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    urls = bottle.request.query.getall("url")  # pylint: disable=no-member
    components = bottle.request.query.getall("component")  # pylint: disable=no-member
    key = json.dumps(dict(metric=metric_name, source=source_name, urls=urls, components=components))
    report_date_string = bottle.request.query.get("report_date")  # pylint: disable=no-member
    report_date = datetime.datetime.fromisoformat(report_date_string.replace("Z", "+00:00")) \
        if report_date_string else datetime.datetime.now(datetime.timezone.utc)
    table = DATABASE["measurements"]
    rows = list(table.find(table.table.columns.timestamp < report_date, key=key, order_by="timestamp")) if table else []
    logging.info("Found %d measurements for %s", len(rows), bottle.request.url)
    return dict(measurements=[json.loads(row["measurement"]) for row in rows])


def import_report():
    """Read the example report and store it in de database."""
    with open("example-report.json") as json_report:
        report = json.load(json_report)
    subjects_table = DATABASE["subjects"]
    metrics_table = DATABASE["metrics"]
    for subject in report["subjects"]:
        subject_row = subjects_table.find_one(title=subject["title"])
        if subject_row:
            subject_id = subject_row["id"]
        else:
            subject_id = subjects_table.insert(dict(title=subject["title"]))
        for metric in subject["metrics"]:
            metric_row = metrics_table.find_one(subject=subject_id, url=metric)
            if not metric_row:
                metrics_table.insert(dict(subject=subject_id, url=metric))
    logging.info("Report consists of %d subjects and %d metrics", len(subjects_table), len(metrics_table))


def serve() -> None:
    """Start the metric-source API which functions as a facade to get metric data from different sources in a
    consistent manner."""
    logging.getLogger().setLevel(logging.INFO)
    global DATABASE
    os.environ.setdefault("DATABASE_URL", "postgresql://postgres:mysecretpassword@localhost:5432/postgres")
    DATABASE = dataset.connect(engine_kwargs=dict(poolclass=NullPool))
    logging.info("Connected to database: %s", DATABASE)

    while True:
        try:
            logging.info("Measurements table has %d measurements", len(DATABASE["measurements"]))
            break
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Waiting for database to become available: %s", reason)
        time.sleep(2)
    import_report()
    bottle.run(server="gevent", host='0.0.0.0', port=8080, reloader=True)


if __name__ == "__main__":
    serve()
