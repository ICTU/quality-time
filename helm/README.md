# Helm chart

## Uninstall

    helm uninstall quality-time

## Install

    helm install quality-time .
    helm install --set pullsecret=mybase64encodeddockerjson quality-time .
    helm install --values myoverride-values.yaml quality-time . 

