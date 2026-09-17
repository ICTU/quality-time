# update-time: allow[hash-drift]
FROM mongo:8.3.11@sha256:5d7043a4ffe02b9ed1b6e0bab057546981af5ca0a79107e9c461e49bc44c0a7b

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time database"

# Harden the base MongoDB image: remove unused tooling that ships known vulnerabilities, and make the data directories
# group-writable so the container can run as a non-root/arbitrary UID. See README.md ("Container hardening") for the
# full rationale, CVE references, and when each workaround can be removed.
RUN apt-get purge --yes mongodb-database-tools mongodb-org-database-tools-extra && \
    apt-get purge --yes --allow-remove-essential ncurses-bin gzip && \
    rm -rf /usr/local/bin/gosu && \
    rm -rf /opt/js-yaml /js-yaml.js && \
    chgrp -R 0 /data/db /data/configdb && \
    chmod -R g=u /data/db /data/configdb

# Run as the non-root MongoDB user by default; see README.md ("Runtime user") for overriding the UID.
USER 999
