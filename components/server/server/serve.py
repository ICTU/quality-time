"""Quality-time server."""

import datetime
import json
import logging
import time
import urllib.parse

import dataset
import bottle


CONNECTION_STRING = "postgresql://postgres:mysecretpassword@postgres:5432/postgres"
DATABASE = None


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
    request_url = measurement["request"]["request_url"]
    table = DATABASE["measurements"]
    table.insert(dict(timestamp=timestamp, request_url=request_url, measurement=json.dumps(measurement)))


@bottle.get("/<metric_name>/<source_name>")
def get(metric_name: str, source_name: str):
    """Handler for the get-metric-from-source API."""
    logging.info(bottle.request)
    bottle.response.add_header("Access-Control-Allow-Origin", "*")
    table = DATABASE["measurements"]
    _, _, path, query, fragment = urllib.parse.urlsplit(bottle.request.url)
    request_url = urllib.parse.urlunsplit(("", "", path, query, fragment)).strip("/")
    try:
        return json.loads(table.find_one(request_url=request_url, order_by="-timestamp")["measurement"])
    except:
        logging.error("Can't find measurement for %s. Table has %d entries", request_url, len(table))
        raise


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
