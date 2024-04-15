#!/bin/sh

set -eu

LC_ALL=C
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

envsubst < /srv/qualitytime.conf.template > /etc/nginx/conf.d/qualitytime.conf

echo "Workaround for the fact that NGINX listen-directive does not take a variable."
