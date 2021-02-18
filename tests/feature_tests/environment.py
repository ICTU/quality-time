"""Code to run before and after certain events during testing."""

import time
from typing import Dict

import requests


def before_all(context):
    """Create shortcuts to send requests to the server API."""

    def cookies():
        """Return the cookies."""
        return dict(session_id=context.session_id) if context.session_id else {}

    def get(api, headers=None, internal=False):
        """Get the resource."""
        base_api_url = context.base_api_url.format("internal-" if internal else "")
        if context.report_date:
            api += f"?report_date={context.report_date}"
        context.response = response = requests.get(f"{base_api_url}/{api}", headers=headers)
        return response.json() if response.headers.get("Content-Type") == "application/json" else response

    def post(api, json=None, internal=False):
        """Post the resource."""
        base_api_url = context.base_api_url.format("internal-" if internal else "")
        context.response = response = requests.post(f"{base_api_url}/{api}", json=json, cookies=cookies())
        if not response.ok:
            return response
        if "session_id" in response.cookies:
            context.session_id = response.cookies["session_id"]
        time.sleep(1)  # Give server and database time to process the previous request
        return response.json()

    def delete(api):
        """Delete the resource."""
        context.response = response = requests.delete(f"{context.base_api_url.format('')}/{api}", cookies=cookies())
        time.sleep(1)  # Give server and database time to process the previous request
        return response.json()

    context.base_api_url = "http://localhost:5001/{0}api/v3"
    context.session_id = None
    context.report_date = None
    context.response = None
    context.uuid: Dict[str, str] = {}  # Keep track of the most recent uuid per item type
    context.get = get
    context.post = post
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
    context.faulty_public_key = """-----BEGIN PUBLIC KEY-----
MIIBtjCCASsGByqGSM44BAEwggEeAoGBAN2YsbQRxa3noHUehRXbDaTmCQCsBW6D
Gy4Yo/Rzg1O6S4gBrk9/h64V3ZcNzKgh3G73v5nReLJo545vq5ZdglRxVqRzEkvK
ecbRrKJfSL/Ir6+utojcBte9u8mK8VBzOEzu3d9VMXhohnLc8AKJgoVz2VLYboHb
DDqil8n5GA81AhUA1zdcpHIsos80Xr8W67v+zc1NugMCgYBO9ui2yfUJK67P3yKm
5kcD7owtqdrgEWo3zPSU94Dyq83ZKnQCqW4jyNVvLHE8vorfrzQG05yxA27fh9y3
13CqD3+SRs1/bh+OoHTYfOg5nQpd+wmpD1KcliwozSa4UoB6L0HGSsmdfDMnyjY6
57A/6fvkIPfFWwiZqDw/UbvXJAOBhAACgYAClAnMuoF2cRmHIkgx7rkBtQQDUuL+
w+tVREFni2i1NBgXEN18fFRtebuPKJvoY0ISQgR+XPoKsgfnQ7jy8bsoZvrto3CP
pwEguMmZYw493abU3P4d66wDe/sFyNLW0rhIx+sYsQ6YhGVWF46peoFC3Aa2H439
frfI8VlILbIxGw==
-----END PUBLIC KEY-----"""


def before_step(context, step):
    """Make the step available in the context."""
    context.step = step
