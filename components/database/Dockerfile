# update-time: allow[hash-drift]
FROM mongo:8.3.8@sha256:5211c51171f57ae60842b11664bb244628971b3d35325762a97888337b9bb0db

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time database"

# Harden the base MongoDB image: remove unused tooling that ships known vulnerabilities, upgrade libraries to the
# latest Ubuntu security fixes ahead of the base image, and make the data directories group-writable so the container
# can run as a non-root/arbitrary UID. The upgrades are guarded to fail the build once the base image makes them
# redundant. See README.md ("Container hardening") for the full rationale, CVE references, and when each workaround
# can be removed. The DL3008 ignore is explained there too.
# hadolint ignore=DL3008
RUN fix="remove the manual upgrade from this Dockerfile." && \
    redundant=0 && \
    set -- && \
    for spec in \
        libcurl4t64=8.5.0-2ubuntu10.13 \
        libp11-kit0=0.25.3-4ubuntu2.2 \
        libssl3t64=3.0.13-0ubuntu3.15 \
        openssl=3.0.13-0ubuntu3.15 \
        perl-base=5.38.2-3.2ubuntu0.4; \
    do \
        package="${spec%%=*}"; \
        if ! installed="$(dpkg-query --showformat='${Version}' --show "$package" 2>/dev/null)"; then \
            echo "ERROR: base image no longer ships $package; $fix" >&2; \
            redundant=1; \
        elif dpkg --compare-versions "$installed" ge "${spec#*=}"; then \
            echo "ERROR: base image already ships $package $installed; $fix" >&2; \
            redundant=1; \
        else \
            set -- "$@" "$package"; \
        fi; \
    done && \
    [ "$redundant" -eq 0 ] && \
    apt-get update && \
    apt-get purge --yes mongodb-database-tools mongodb-org-database-tools-extra && \
    apt-get purge --yes --allow-remove-essential ncurses-bin gzip && \
    apt-get install --only-upgrade --yes --no-install-recommends "$@" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/local/bin/gosu && \
    rm -rf /opt/js-yaml /js-yaml.js && \
    chgrp -R 0 /data/db /data/configdb && \
    chmod -R g=u /data/db /data/configdb

# Run as the non-root MongoDB user by default; see README.md ("Runtime user") for overriding the UID.
USER 999
