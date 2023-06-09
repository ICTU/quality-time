"""Initialize bottle."""

import bottle
from pymongo.database import Database

from shared.routes.plugins import InjectionPlugin

from routes import *  # lgtm [py/unused-import], # noqa: F403
from routes.plugins import AuthPlugin


def init_bottle(database: Database) -> None:
    """Initialize bottle."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    bottle.install(InjectionPlugin(value=database, keyword="database"))
    bottle.install(AuthPlugin())
