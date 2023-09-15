"""Shared code to export reports overview and reports to PDF."""

from urllib import parse

import bottle
import requests

from shared.utils.env import getenv
from shared.utils.type import ReportId


def export_as_pdf(report_uuid: ReportId | None = None):
    """Export the URL as PDF."""
    renderer_host = getenv("RENDERER_HOST")
    renderer_port = getenv("RENDERER_PORT")
    render_url = f"http://{renderer_host}:{renderer_port}/api/render"
    # Tell the frontend to not display toast messages to prevent them from being included in the PDF:
    query_string = "?hide_toasts=true" + (f"&{bottle.request.query_string}" if bottle.request.query_string else "")
    path = parse.quote(f"{report_uuid or ''}{query_string}")
    response = requests.get(f"{render_url}?path={path}", timeout=120)
    response.raise_for_status()
    bottle.response.content_type = "application/pdf"
    return response.content
