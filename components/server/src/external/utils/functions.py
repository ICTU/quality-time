"""Utility functions."""

import re

import bottle
import requests

# Bandit complains that "Using autolink_html to parse untrusted XML data is known to be vulnerable to XML attacks",
# and Dlint complains 'insecure use of XML modules, prefer "defusedxml"'
# but we give autolink_html clean html, so ignore the warning:
from lxml.html.clean import autolink_html, clean_html  # noqa: DUO107, # nosec, pylint: disable=no-name-in-module

from server_utilities.functions import iso_timestamp
from server_utilities.type import URL


def check_url_availability(url: URL, source_parameters: dict[str, str]) -> dict[str, int | str]:
    """Check the availability of the URL."""
    credentials = _basic_auth_credentials(source_parameters)
    headers = _headers(source_parameters)
    try:
        response = requests.get(url, auth=credentials, headers=headers, verify=False)  # noqa: DUO123, # nosec
        return dict(status_code=response.status_code, reason=response.reason)
    except Exception as exception_instance:  # pylint: disable=broad-except
        exception_reason = str(exception_instance) or exception_instance.__class__.__name__
        # If the reason contains an errno, only return the errno and accompanying text, and leave out the traceback
        # that led to the error:
        exception_reason = re.sub(r".*(\[errno \-?\d+\] [^\)^']+).*", r"\1", exception_reason, flags=re.IGNORECASE)
        return dict(status_code=-1, reason=exception_reason)


def _basic_auth_credentials(source_parameters) -> tuple[str, str] | None:
    """Return the basic authentication credentials, if any."""
    if private_token := source_parameters.get("private_token", ""):
        return private_token, ""
    username = source_parameters.get("username", "")
    password = source_parameters.get("password", "")
    return (username, password) if username or password else None


def _headers(source_parameters) -> dict:
    """Return the headers for the url-check."""
    return {"Private-Token": source_parameters["private_token"]} if "private_token" in source_parameters else {}


def report_date_time() -> str:
    """Return the report date requested as query parameter if it's in the past, else return an empty string."""
    if report_date_string := dict(bottle.request.query).get("report_date"):
        iso_report_date_string = str(report_date_string).replace("Z", "+00:00")
        if iso_report_date_string < iso_timestamp():
            return iso_report_date_string
    return ""


def sanitize_html(html_text: str) -> str:
    """Clean dangerous tags from the HTML and convert urls into anchors."""
    sanitized_html = str(autolink_html(clean_html(html_text)))
    # The clean_html function creates HTML elements. That means if the user enters a simple text string it gets
    # enclosed in a <p> tag. Remove it to not confuse users that haven't entered any HTML:
    if sanitized_html.count("<") == 2:
        sanitized_html = re.sub("</?p>", "", sanitized_html)
    return sanitized_html
