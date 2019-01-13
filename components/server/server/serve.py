"""Quality-time server."""

from gevent import monkey
monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import datetime
import json
import logging
import time

import bottle
import pymongo


DATABASE = None


@bottle.get("/report")
def get_report():
    """Return the quality report."""
    logging.info(bottle.request)
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    report = DATABASE.reports.find_one({})
    report["_id"] = str(report["_id"])
    return report


@bottle.post("/measurement")
def post_measurement() -> None:
    """Put the measurement in the database."""
    def equal_measurements(measure1, measure2):
        """Return whether the measurements have equal values and targets."""
        return measure1["measurement"] == measure2["measurement"] and \
               measure1["target"] == measure2["target"] and \
               measure1["status"] == measure2["status"] and \
               measure1["calculation_error"] == measure2["calculation_error"]

    logging.info(bottle.request)
    measurement = bottle.request.json
    timestamp_string = measurement["measurement"]["timestamp"]
    latest_measurement_doc = DATABASE.measurements.find_one(
        filter={"request.request_url": measurement["request"]["request_url"]},
        sort=[("measurement.start", pymongo.DESCENDING)])
    if latest_measurement_doc:
        if equal_measurements(latest_measurement_doc["measurement"], measurement["measurement"]):
            DATABASE.measurements.update_one(
                filter={"_id": latest_measurement_doc["_id"]},
                update={"$set": {"measurement.end": timestamp_string}})
            return
        comment = latest_measurement_doc["comment"]  # Reuse comment of previous measurement
    else:
        comment = measurement["comment"]
    measurement["measurement"]["start"] = timestamp_string
    measurement["measurement"]["end"] = timestamp_string
    measurement["comment"] = comment
    del measurement["measurement"]["timestamp"]
    DATABASE.measurements.insert_one(measurement)


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
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    comment = bottle.request.json.get("comment", "")
    urls = bottle.request.query.getall("url")  # pylint: disable=no-member
    components = bottle.request.query.getall("component")  # pylint: disable=no-member
    latest_measurement_doc = DATABASE.measurements.find_one(
        filter={"request.metric": metric_name, "request.source": source_name,
                "request.urls": urls, "request.components": components},
        sort=[("measurement.start", pymongo.DESCENDING)])
    if not latest_measurement_doc:
        logging.error("Can't find measurement for comment %s with parameters %s, %s, %s, %s",
                      comment, metric_name, source_name, urls, components)
        return
    del latest_measurement_doc['_id']
    latest_measurement_doc["comment"] = comment
    timestamp_string = datetime.datetime.now(datetime.timezone.utc).isoformat()
    latest_measurement_doc["measurement"]["start"] = timestamp_string
    latest_measurement_doc["measurement"]["end"] = timestamp_string
    DATABASE.measurements.insert_one(latest_measurement_doc)
    return dict()


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
    data = DATABASE.measurements.count_documents({})
    yield sse_pack(event_id, "init", data)

    # Now give the client updates as they arrive
    while True:
        time.sleep(10)
        new_data = DATABASE.measurements.count_documents({})
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
    report_date_string = bottle.request.query.get("report_date")  # pylint: disable=no-member
    report_date_string = report_date_string.replace("Z", "+00:00") \
        if report_date_string else datetime.datetime.now(datetime.timezone.utc).isoformat()
    docs = DATABASE.measurements.find(
        filter={"request.metric": metric_name, "request.source": source_name,
                "request.urls": urls, "request.components": components,
                "measurement.start": {"$lt": report_date_string}})
    logging.info("Found %d measurements for %s", docs.count(), bottle.request.url)
    measurements = []
    for measurement in docs:
        measurement["_id"] = str(measurement["_id"])
        measurements.append(measurement)
    return dict(measurements=measurements)


def import_report():
    """Read the example report and store it in the database."""
    # Until reports can be configured via the front-end, we load an example report on start up
    # and replace the existing report in the database, if any.
    with open("example-report.json") as json_report:
        report = json.load(json_report)
    DATABASE.reports.replace_one({}, report, upsert=True)
    stored_report = DATABASE.reports.find_one({})
    nr_subjects = len(stored_report["subjects"])
    nr_metrics = sum([len(subject["metrics"]) for subject in stored_report["subjects"]])
    logging.info("Report consists of %d subjects and %d metrics", nr_subjects, nr_metrics)


def serve() -> None:
    """Start the metric-source API which functions as a facade to get metric data from different sources in a
    consistent manner."""
    logging.getLogger().setLevel(logging.INFO)
    global DATABASE
    DATABASE = pymongo.MongoClient("mongodb://root:root@localhost:27017/").quality_time_db
    logging.info("Connected to database: %s", DATABASE)

    while True:
        try:
            logging.info("Measurements collection has %d measurements", DATABASE.measurements.count_documents({}))
            break
        except Exception as reason:  # pylint: disable=broad-except
            logging.warning("Waiting for database to become available: %s", reason)
        time.sleep(2)
    import_report()
    bottle.run(server="gevent", host='0.0.0.0', port=8080, reloader=True)


if __name__ == "__main__":
    serve()
