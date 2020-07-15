"""Code to run before and after certain events during testing."""

import time
from typing import Dict

import requests


BASE_API_URL = "http://localhost:5001/api/v3"


def before_all(context):
    """Create shortcuts to send requests to the server API."""

    def cookies():
        """Return the cookies."""
        return dict(session_id=context.session_id) if context.session_id else dict()

    def get(api):
        """Get the resource."""
        return requests.get(f"{BASE_API_URL}/{api}").json()

    def post(api, json=None):
        """Post the resource."""
        result = requests.post(f"{BASE_API_URL}/{api}", json=json, cookies=cookies())
        if "session_id" in result.cookies:
            context.session_id = result.cookies["session_id"]
        time.sleep(1)  # Give server and database time to process the previous request
        return result.json()

    def delete(api):
        """Delete the resource."""
        result = requests.delete(f"{BASE_API_URL}/{api}", cookies=cookies())
        time.sleep(1)  # Give server and database time to process the previous request
        return result.json()

    context.session_id = None
    context.uuid: Dict[str, str] = {}  # Keep track of the most recent uuid per item type
    context.get = get
    context.post = post
    context.delete = delete
