# update-time: allow[digest-drift]
FROM debian:13.6-slim@sha256:020c0d20b9880058cbe785a9db107156c3c75c2ac944a6aa7ab59f2add76a7bd

# Install slapd and requirements
RUN \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    gettext-base \
    ldap-utils \
    openssl \
    slapd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /etc/ldap/ssl /bootstrap

COPY *.sh /
COPY bootstrap /bootstrap

EXPOSE 389 636

CMD ["/bin/bash", "/run.sh"]
ENTRYPOINT []
