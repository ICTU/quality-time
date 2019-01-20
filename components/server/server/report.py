"""Report routes."""

import bottle


@bottle.get("/report/title")
def get_report_title(database):
    """Return the report title."""
    return dict(title=database.reports.find_one(filter={})["title"])


@bottle.post("/report/title")
def post_report_title(database):
    """Set the report title."""
    title = bottle.request.json.get("title", "Quality-time")
    database.reports.update_one(filter={}, update={"$set": {"title": title}})


@bottle.get("/report")
def get_report(database):
    """Return the quality report."""
    report = database.reports.find_one({})
    report["_id"] = str(report["_id"])
    return report
