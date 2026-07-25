# update-time: allow[digest-drift]
FROM mongo:8.3.4@sha256:309d760ba3f7962e14d54ac6123c7fe72ed2d465196b4d0eaf8abcea7dd39450

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time database"

# Harden the base MongoDB image: remove unused tooling that ships known vulnerabilities, upgrade libraries to the
# latest Ubuntu security fixes ahead of the base image, and make the data directories group-writable so the container
# can run as a non-root/arbitrary UID. Each step is guarded to fail the build once the base image makes it redundant.
# See README.md ("Container hardening") for the full rationale, CVE references, and when each workaround can be removed.
# The DL3008/SC2086 ignores are explained there too.
# hadolint ignore=DL3008,SC2086
RUN PACKAGE_VERSIONS="\
        libnghttp2-14 1.59.0-1ubuntu0.4 \
        libncursesw6 6.4+20240113-1ubuntu2.1 \
        libtinfo6 6.4+20240113-1ubuntu2.1 \
        ncurses-base 6.4+20240113-1ubuntu2.1 \
        perl-base 5.38.2-3.2ubuntu0.3 \
        tar 1.35+dfsg-3ubuntu0.1" && \
    set -- $PACKAGE_VERSIONS && \
    packages="" && \
    while [ "$#" -gt 0 ]; do \
        installed="$(dpkg-query --showformat='${Version}' --show "$1")" && \
        if dpkg --compare-versions "$installed" ge "$2"; then \
            echo "ERROR: base image already ships $1 $installed; remove the manual upgrade from this Dockerfile." >&2; \
            exit 1; \
        fi; \
        packages="$packages $1"; \
        shift 2; \
    done && \
    apt-get update && \
    apt-get purge --yes mongodb-database-tools mongodb-org-database-tools-extra && \
    apt-get purge --yes --allow-remove-essential ncurses-bin gzip && \
    apt-get install --only-upgrade --yes --no-install-recommends $packages && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/local/bin/gosu && \
    chgrp -R 0 /data/db /data/configdb && \
    chmod -R g=u /data/db /data/configdb

# Run as the non-root MongoDB user by default; see README.md ("Runtime user") for overriding the UID.
USER 999
