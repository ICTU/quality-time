# update-time: allow[hash-drift]
FROM mongo:9.0.8@sha256:b0c835c26e5997413e985000f1013c275377cd9607761c1784d486f6dd620b7f

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
        libc-bin=2.43-2ubuntu2.7 \
        libc-gconv-modules-extra=2.43-2ubuntu2.7 \
        libc6=2.43-2ubuntu2.7 \
        libgssapi-krb5-2=1.22.1-2ubuntu4.3 \
        libk5crypto3=1.22.1-2ubuntu4.3 \
        libkrb5-3=1.22.1-2ubuntu4.3 \
        libkrb5support0=1.22.1-2ubuntu4.3 \
        perl-base=5.40.1-7ubuntu0.4; \
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
    apt-get --option Acquire::Retries=3 update && \
    apt-get purge --yes mongodb-database-tools mongodb-org-database-tools-extra krb5-locales && \
    apt-get purge --yes --allow-remove-essential ncurses-bin gzip && \
    apt-get --option Acquire::Retries=3 install --only-upgrade --yes --no-install-recommends "$@" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/bin/pebble /var/lib/pebble && \
    rm -rf /usr/local/bin/gosu && \
    rm -rf /opt/js-yaml /js-yaml.js && \
    chgrp -R 0 /data/db /data/configdb && \
    chmod -R g=u /data/db /data/configdb

# Run as the non-root MongoDB user by default; see README.md ("Runtime user") for overriding the UID.
USER 999

# Log less than mongod does by default; see README.md ("Logging").
CMD ["mongod", "--quiet", "--wiredTigerEngineConfigString=verbose=[]"]
