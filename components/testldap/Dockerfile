# update-time: allow[hash-drift]
FROM debian:13.7-slim@sha256:a99cfc517144bc59b1978475ec53b46ecabec7e43635402ee5b77cc54cd1b20a

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
