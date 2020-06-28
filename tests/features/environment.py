"""Code to run before and after certain events during testing."""

import os
import shutil
import subprocess  # nosec

import requests


def before_all(context):
    """Create a shortcut for to get an API."""
    def get():
        """Get the API."""
        result = requests.get(f"http://localhost:5001/api/v3/{context.api}")
        return result.json()
    context.get = get

