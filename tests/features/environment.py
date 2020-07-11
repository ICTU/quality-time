"""Code to run before and after certain events during testing."""

import requests


BASE_API_URL = "http://localhost:5001/api/v3"


def before_all(context):
    """Create shortcuts send requests to the server API."""

    def get():
        """Get the API."""
        result = requests.get(f"{BASE_API_URL}/{context.api}")
        return result.json()

    def post(api, json=None):
        """Post the data."""
        cookies = dict(session_id=context.session_id) if context.session_id else dict()
        result = requests.post(f"{BASE_API_URL}/{api}", json=json, cookies=cookies)
        if "session_id" in result.cookies:
            context.session_id = result.cookies["session_id"]
        return result.json()

    context.session_id = None
    context.get = get
    context.post = post
