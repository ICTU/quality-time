FROM mongo:8.3.4@sha256:0f887198e29c093fd2b36c3e2eb43c7b98e47c081d89fbd5bc212da0cd43ec58

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time database"

# Remove the MongoDB database tools (mongodump, mongorestore, mongoexport, mongostat, etc.). They are not used
# by the server, by Quality-time (the components connect via PyMongo), or for backups (which use a separate
# mongo container, see the deployment documentation), and they ship with their own vulnerabilities. The server
# (mongod) and the shell (mongosh, needed by the entrypoint to create the root user) are kept.
# Make the data directories group-owned by the root group (GID 0) and group-writable so the container can run
# as an arbitrary non-root user (some platforms, such as OpenShift, assign a random high UID with GID 0). This,
# combined with running as non-root, means gosu is no longer needed and can be removed to reduce the attack surface.
# Upgrade several libraries to pick up the latest Ubuntu security fixes; the MongoDB base image lags behind the Ubuntu
# security updates. Each guard fails the build once the base image itself ships the fixed version, signalling that
# workaround can be removed; bump the version in a guard whenever a newer fix needs to be pulled in.
# The base image also bundles js-yaml 3.13.1 (/opt/js-yaml, symlinked as /js-yaml.js) solely so the entrypoint can
# parse a mongod YAML config passed via --config. Quality-time never passes --config (see docker-compose.yml and the
# Helm chart), so this parser is unreachable here, yet it carries CVE-2025-64718 (prototype pollution). Remove it to
# drop the finding and shrink the attack surface; its guard fails the build if the base image stops shipping js-yaml
# at this path, signalling that this cleanup can be removed.
# DL3008 (pin apt versions) is intentionally ignored: --only-upgrade pulls the latest security patch rather
# than a fixed version, and the guards above bound the minimum. SC2086 is ignored for the deliberate word-split
# of "package min-version" pairs in the loop.
# hadolint ignore=DL3008,SC2086
RUN PACKAGE_VERSIONS="\
        libgnutls30t64 3.8.3-1.1ubuntu3.6 \
        libudev1 255.4-1ubuntu8.16 \
        libgcrypt20 1.10.3-2ubuntu0.1 \
        liblzma5 5.6.1+really5.4.5-1ubuntu0.3 \
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
    apt-get install --only-upgrade --yes --no-install-recommends $packages && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/local/bin/gosu && \
    chgrp -R 0 /data/db /data/configdb && \
    chmod -R g=u /data/db /data/configdb && \
    if [ ! -e /opt/js-yaml/package.json ]; then \
        echo "ERROR: /opt/js-yaml not found; remove this cleanup from the Dockerfile." >&2; \
        exit 1; \
    fi && \
    rm -rf /opt/js-yaml /js-yaml.js

# Run as the non-root MongoDB user by default. Platforms that require a UID >= 1000 can override this with a
# securityContext (see the deployment documentation); the data directories above are group-writable for GID 0.
USER 999
