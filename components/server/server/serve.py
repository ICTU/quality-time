"""Quality-time server."""

from gevent import monkey; monkey.patch_all()

import datetime
import json
import logging
import time
import urllib.parse

import dataset
import bottle


CONNECTION_STRING = "postgresql://postgres:mysecretpassword@database:5432/postgres"
DATABASE = None


def key(measurement) -> str:
    """Create a database key from the measurement."""
    request = measurement["request"]
    return json.dumps(dict(metric=request["metric"], source=request["source"],
                           urls=request["urls"], components=request["components"]))


def sse_pack(data):
    """Pack data in Server-Sent Events (SSE) format"""
    buffer = ""
    for key in ["retry", "id", "event", "data"]:
        if key in data.keys():
            buffer += f"{key}: {data[key]}\n"
    return buffer + "\n"


@bottle.get("/report")
def report():
    """Return the quality report."""
    logging.info(bottle.request)
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    with open("example-report.json") as json_report:
        return json.load(json_report)


@bottle.post("/measurement")
def post():
    """Put the measurement in the database."""
    def equal_measurements(m1, m2):
        """Return whether the measurements have equal values and targets."""
        return m1["measurement"] == m2["measurement"] and m1["target"] == m2["target"] and \
            m1["status"] == m2["status"] and m1["calculation_error"] == m2["calculation_error"]

    logging.info(bottle.request)
    measurement = bottle.request.json
    timestamp_string = measurement["measurement"]["timestamp"]
    measurement["measurement"]["start"] = timestamp_string
    measurement["measurement"]["end"] = timestamp_string
    timestamp = datetime.datetime.fromisoformat(timestamp_string)
    table = DATABASE["measurements"]
    latest_measurement_row = table.find_one(key=key(measurement), order_by="-timestamp")
    latest_measurement = json.loads(latest_measurement_row["measurement"])
    if latest_measurement and equal_measurements(latest_measurement["measurement"], measurement["measurement"]):
        latest_measurement["measurement"]["end"] = timestamp_string
        table.update(dict(id=latest_measurement_row["id"], timestamp=timestamp,
                          measurement=json.dumps(latest_measurement)), ["id"])
    else:
        table.insert(dict(timestamp=timestamp, key=key(measurement), measurement=json.dumps(measurement)))


@bottle.route("/nr_measurements", method="OPTIONS")
def options():
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    bottle.response.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    bottle.response.set_header("Access-Control-Allow-Headers", "X-REQUESTED-WITH, CACHE-CONTROL, LAST-EVENT-ID")
    bottle.response.set_header("Content-Type", "text/plain")
    return ""


@bottle.get("/nr_measurements")
def stream_generator():
    # Keep event IDs consistent
    event_id = 0
    if "Last-Event-Id" in bottle.request.headers:
        event_id = int(bottle.request.headers["Last-Event-Id"]) + 1

    # Set up our message payload with a retry value in case of connection failure
    # (that's also the polling interval to be used as fallback by our polyfill)
    msg = dict(retry="2000")

    # Provide an initial data dump to each new client
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    bottle.response.set_header("Content-Type", "text/event-stream")
    data = len(DATABASE["measurements"])
    msg.update(dict(event="init", data=data, id=event_id))
    yield sse_pack(msg)

    # Now give them deltas as they arrive (say, from a message broker)
    msg["event"] = "delta"
    while True:
        # block until you get new data (from a queue, pub/sub, zmq, etc.)
        time.sleep(10)
        if len(DATABASE["measurements"]) > data:
            data = len(DATABASE["measurements"])
            event_id += 1
            msg.update(dict(data=data, id=event_id))
            yield sse_pack(msg)


@bottle.get("/<metric_name>/<source_name>")
def get(metric_name: str, source_name: str):
    """Handler for the get-metric-from-source API."""
    logging.info(bottle.request)
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    table = DATABASE["measurements"]
    if len(table) == 0:
        logging.warning("There are no measurements in the database yet.")
        return
    urls = bottle.request.query.getall("url")
    components = bottle.request.query.getall("component")
    key = json.dumps(dict(metric=metric_name, source=source_name, urls=urls, components=components))
    report_date_string = bottle.request.query.get("report_date")
    report_date = datetime.datetime.fromisoformat(report_date_string) if report_date_string else datetime.datetime.now()
    measurement = table.find_one(table.table.columns.timestamp <= report_date, key=key, order_by="-timestamp")
    if measurement:
        logging.info("Found measurement for %s: %s", bottle.request.url, measurement)
        return json.loads(measurement["measurement"])
    logging.warning("Couldn't find measurement for %s, key=%s, report_date=%s", bottle.request.url, key, report_date)


def serve():
    """Start the metric-source API which functions as a facade to get metric data from different sources in a
    consistent manner."""
    logging.getLogger().setLevel(logging.INFO)
    global DATABASE
    DATABASE = dataset.connect(CONNECTION_STRING)
    logging.info("Connected to database: %s", DATABASE)
    while True:
        try:
            logging.info("Measurements table has %d measurements", len(DATABASE["measurements"]))
            break
        except Exception as reason:
            logging.warning("Waiting for database to become available: %s", reason)
        time.sleep(2)
    bottle.run(server="gevent", host='0.0.0.0', port=8080, reloader=True)


if __name__ == "__main__":
    serve()
