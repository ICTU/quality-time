# Helm chart

A Helm chart allows for a simple deployment on a Kubernetes cluster. The Helm chart in this directory is based on the docker-compose.yml and the standard images and settings from ICTU.
Except for the Route these are all standard kubernetes elements. The Route defines the main entry point for the application on OpenShift. It is added as the last element in the [templates/www-service.yaml](templates/www-service.yaml).
Also in a corporate environment, it is usually required to define credentials for pulling the images. For this a [templates/pull-secret.yaml](templates/pull-secret.yaml) file is provided.
All templates refer to standard values from [values.yaml](values.yaml) unless these are overridden using the Helm way of value overrides. (Either by defining seperate values or your own values.yaml file).

## Prerequisites

You need the following CLI tools:

+ OC CLI the OpenShift cli
+ Helm the Helm CLI

Login with the OC CLI and select a project/namespace. Then the helm commands can be used.

## Install

```console
$ helm install quality-time .
$ helm install --set pullsecret=mybase64encodeddockerjson quality-time .
$ helm install --values myoverride-values.yaml quality-time .
```

## Uninstall

```console
$ helm uninstall quality-time
```

In a corporate environment with custom certificate authorities, you can create custom images as described in the [Custom docker files Readme](../dockerfiles/README.md).
The adjusted image names can then be set in the myoverride-values.yaml which would be a kind of copy of the values.yaml.
