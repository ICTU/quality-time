# update-time: allow[digest-drift]
FROM mongo:8.3.7@sha256:2f02e2184c6d91c3208e5ab75a0707d1386a05377b20fdaf49a314815774d863

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time database"

# Harden the base MongoDB image: remove unused tooling that ships known vulnerabilities, and make the data directories
# group-writable so the container can run as a non-root/arbitrary UID.
# See README.md ("Container hardening") for the full rationale, CVE references, and when each workaround can be removed.
RUN apt-get update && \
    apt-get purge --yes mongodb-database-tools mongodb-org-database-tools-extra && \
    apt-get purge --yes --allow-remove-essential ncurses-bin gzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/local/bin/gosu && \
    chgrp -R 0 /data/db /data/configdb && \
    chmod -R g=u /data/db /data/configdb

# Run as the non-root MongoDB user by default; see README.md ("Runtime user") for overriding the UID.
USER 999
