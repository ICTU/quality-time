"""Quality-time server."""

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


@bottle.get("/report")
def report():
    """Return the quality report."""
    logging.info(bottle.request)
    bottle.response.add_header("Access-Control-Allow-Origin", "*")
    with open("example-report.json") as json_report:
        return json.load(json_report)


@bottle.post("/measurement")
def post():
    """Put the measurement in the database."""
    logging.info(bottle.request)
    measurement = bottle.request.json
    timestamp = datetime.datetime.fromisoformat(measurement["measurement"]["timestamp"])
    table = DATABASE["measurements"]
    table.insert(dict(timestamp=timestamp, key=key(measurement), measurement=json.dumps(measurement)))


@bottle.get("/<metric_name>/<source_name>")
def get(metric_name: str, source_name: str):
    """Handler for the get-metric-from-source API."""
    logging.info(bottle.request)
    bottle.response.add_header("Access-Control-Allow-Origin", "*")
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
    bottle.run(server="cherrypy", host='0.0.0.0', port=8080, reloader=True)


if __name__ == "__main__":
    serve()
