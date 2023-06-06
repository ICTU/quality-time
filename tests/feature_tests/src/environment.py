"""Code to run before and after certain events during testing."""

from typing import Any

import pymongo
import requests
from behave.model import Step
from behave.runner import Context


def before_all(context: Context) -> None:  # noqa: C901
    """Create shortcuts to send requests to the server API."""
    timeout = 10

    def cookies() -> dict[str, str]:
        """Return the cookies."""
        return {"session_id": context.session_id} if context.session_id else {}

    def api_url(api: str, internal: bool = False) -> str:
        """Return the API URL."""
        base_api_url = context.internal_base_api_url if internal else context.base_api_url
        return f"{base_api_url}/{api}"

    def get(api: str, headers: dict[str, str] | None = None, internal: bool = False) -> requests.Response | Any:
        """Get the resource."""
        url = api_url(api, internal)
        for attribute in ("report_date", "min_report_date"):
            if value := getattr(context, attribute):
                sep = "&" if "?" in url else "?"
                url += f"{sep}{attribute}={value}"
        context.response = response = requests.get(url, headers=headers, cookies=cookies(), timeout=timeout)
        return response.json() if response.headers.get("Content-Type") == "application/json" else response

    def post(api: str, json: dict | list | None = None, internal: bool = False) -> requests.Response | Any:
        """Post the resource."""
        url = api_url(api, internal)
        response = requests.post(url, json=json, cookies=cookies(), timeout=timeout)
        context.post_response = context.response = response
        if not response.ok:
            return response
        if "session_id" in response.cookies:
            context.session_id = response.cookies["session_id"]
        return response.json() if response.headers.get("Content-Type") == "application/json" else response

    def put(api: str, json: dict | list | None = None, internal: bool = False) -> requests.Response | Any:
        """Post the resource."""
        url = api_url(api, internal)
        response = requests.put(url, json=json, cookies=cookies(), timeout=timeout)
        context.put_response = context.response = response
        # Ignore non-ok responses for now since we don't have testcases where they apply
        return response.json() if response.headers.get("Content-Type") == "application/json" else response

    def delete(api: str) -> requests.Response | Any:
        """Delete the resource."""
        context.response = response = requests.delete(api_url(api), cookies=cookies(), timeout=timeout)
        return response.json() if response.headers.get("Content-Type") == "application/json" else response

    context.base_api_url = "http://localhost:5001/api/v3"
    context.internal_base_api_url = "http://localhost:5002/api"
    context.database = pymongo.MongoClient("mongodb://root:root@localhost:27017")["quality_time_db"]
    context.session_id = None
    context.report_date = None
    context.min_report_date = None
    context.response = None  # Most recent respone
    context.post_response = None  # Most recent post response
    # Create a typed local variable to prevent mypy error: Type cannot be declared in assignment to non-self attribute
    uuid: dict[str, str] = {}
    context.uuid = uuid  # Keep track of the most recent uuid per item type
    context.get = get
    context.post = post
    context.put = put
    context.delete = delete
    context.public_key = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEApLaktGOguW3bcC0xILmf
ToucM7eYx3oXKSKKg2aX8TNwX6qendovmUw0X6ooM+vcKEqL/h8F26RdmvIxoJLa
uK7BrqW4zDlYtLqmnsVE7rXLAFfgc+r8vxhlAvXGZIMqLd6KM/WTJu6+cxDwNJT7
TVr9Fxy6vP7CxqYrzPFcau/iNZQxvUSp8M7vHgRRsF4Ux8uQk2WqEjJ9gFYF6y/l
2MYGTjHSe2FzdzvpmPdwiSeZU42+zd9hqvjNdhc04rxNKu1xvpQthBY2d497Idkg
5380siuYrFMb46VtL3hdIoOH5934/nBVU35aXDirPcoZazMN2D3BaWULeEcvmKq1
pmUcidkMuTLeiOksl/d3GBT6dvdSVEsHG5rg9SB3XCrA3Fk3R1Dp/b9WHZko+tqx
nivGYzlaMI/gzLCiWSiL4FuJIttiqdZM2xWFTHIdpQXO3jmogV2ouYJ/IoDIyIR9
M9uddlTPkf3y6mSLwtl3tJ6eDk4EoWFKc8q8F0hza5PLQD5P8O7ddLZ5SAVEoeLP
oRo4ZewdU/XOhYKw3Jgpj1GFPwO/wxpKmYmjGR7lzG4uzae4o/3pEBi2KnSlUhC9
Fm+YDdqKwPSXu1L2DfJBISqpc2ua29O1WBQlsFo9QfSuESSRBnwvt4IbIwH5CVMJ
hv23LX3At2kFGKAPC0jM1YUCAwEAAQ==
-----END PUBLIC KEY-----
"""


def before_step(context: Context, step: Step) -> None:
    """Make the step available in the context."""
    context.step = step
