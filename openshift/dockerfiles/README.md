# Docker - Podman rebuild for Enterprises 

For companies that use their own certificate authorities, the Dockerfiles supplied in this directory can be used as an example to add ca certificates to trust stores.
Also the proxy image is adjusted so it will be able to run as non-root on openshift.

## podman build

You can build the images from the ICTU base images. so either pull does images or first build these images. Then you can build and tag your extensions.

    podman build -t containers.local/somenamespace/quality-time_proxy:v4.5.0 --build-arg IMAGE_NAME=registry.access.redhat.com/ubi8/nginx-120 -f Dockerfile.proxy .
	
Make sure to adjust the docker-compose.yml or the helm chart values.yml with your extension images.
	
## Changes for custom Certificate Authorities

If your organization uses their own certificate authority, you need to add the certificate to the correct trust stores in the images that have connections to the resources that have certificates that were issued by this certificate authority.

    USER root
    COPY *.crt /usr/local/share/ca-certificates/
    COPY *.crt /etc/ssl/certs/ 
    RUN /usr/sbin/update-ca-certificates
    RUN cd /usr/local/share/ca-certificates/ ; for key in $(ls *.crt) ;do cat $key >> /usr/lib/ssl/cert.pem ; done 
    ENV REQUESTS_CA_BUNDLE /usr/lib/ssl/cert.pem

[Dockerfile.externalserver](./Dockerfile.externalserver) show an example to add the certificate and enable it at OS level and Python application level.

## Changes for non-root process

If you use a strict OpenShift environment it will not be allowed to start processes as a root user or with a fixed user id. The original nginx proxy image is using a root user. 

    FROM registry.access.redhat.com/ubi8/nginx-120

[Dockerfile.proxy](./Dockerfile.proxy) uses a different and OpenShift compliant base image from Red Hat.

## Changes due to non random user id

If you use a strict OpenShift environment it will not be allowed to access files created by a user with a fixed user id. You can rebuild an image to allow access to such files or directories.

    RUN chgrp -R 0 /home/collector && chmod -R g=u /home/collector
	
[Dockerfile.collector](./Dockerfile.collector) shows the fix for this in the collector image.




	

