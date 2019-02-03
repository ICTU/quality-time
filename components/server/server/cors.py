"""Enable Cross Origin Resource Sharing (CORS)."""

import bottle


@bottle.route('/<:re:.*>', method='OPTIONS')
def enable_cors_generic_route():
    """This route takes priority over all others. So any request with an OPTIONS
    method will be handled by this function.

    See: https://github.com/bottlepy/bottle/issues/402

    NOTE: This means we won't 404 any invalid path that is an OPTIONS request."""
    return ""


@bottle.hook('after_request')
def enable_cors_after_request_hook():
    """This executes after every route. We use it to attach CORS headers when applicable."""
    headers = dict(
        Origin="*", Methods="GET, POST, PUT, DELETE, OPTIONS",
        Headers="Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Cache-Control, Last-Event-Id")
    for key, value in headers.items():
        bottle.response.set_header(f"Access-Control-Allow-{key}", value)
