"""Quality-time server."""


def serve(server: str = "gevent") -> None:  # pragma: no cover-behave
    """Connect to the database and start the application server."""
    if server == "gevent":
        from gevent import monkey

        monkey.patch_all()
    import logging
    import os
    import bottle
    from initialization import init_bottle, init_database

    logging.getLogger().setLevel(logging.INFO)
    database = init_database()
    init_bottle(database)
    server_port = os.environ.get("SERVER_PORT", "5001")
    bottle.run(server=server, host="0.0.0.0", port=server_port, reloader=True, log=logging.getLogger())  # nosec


if __name__ == "__main__":  # pragma: no cover-behave
    serve()
