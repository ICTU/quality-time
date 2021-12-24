"""Utility functions."""

import re

# Bandit complains that "Using autolink_html to parse untrusted XML data is known to be vulnerable to XML attacks",
# and Dlint complains 'insecure use of XML modules, prefer "defusedxml"'
# but we give autolink_html clean html, so ignore the warning:
from lxml.html.clean import autolink_html, clean_html  # noqa: DUO107, # nosec, pylint: disable=no-name-in-module


def sanitize_html(html_text: str) -> str:
    """Clean dangerous tags from the HTML and convert urls into anchors."""
    sanitized_html = str(autolink_html(clean_html(html_text)))
    # The clean_html function creates HTML elements. That means if the user enters a simple text string it gets
    # enclosed in a <p> tag. Remove it to not confuse users that haven't entered any HTML:
    if sanitized_html.count("<") == 2:
        sanitized_html = re.sub("</?p>", "", sanitized_html)
    return sanitized_html
