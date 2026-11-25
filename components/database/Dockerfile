# update-time: allow[hash-drift]
FROM mongo:9.0.8@sha256:b0c835c26e5997413e985000f1013c275377cd9607761c1784d486f6dd620b7f

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

# Log less than mongod does by default; see README.md ("Logging").
CMD ["mongod", "--quiet", "--wiredTigerEngineConfigString=verbose=[]"]
