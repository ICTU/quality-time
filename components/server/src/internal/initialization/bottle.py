"""Initialize bottle."""

import bottle
from pymongo.database import Database

from internal.routes.plugins import InjectionPlugin

# isort: off
# pylint: disable=wildcard-import,unused-wildcard-import
from internal.routes import *  # lgtm [py/unused-import]

# isort: on


def init_bottle(database: Database) -> None:
    """Initialize bottle."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    bottle.install(InjectionPlugin(value=database, keyword="database"))
