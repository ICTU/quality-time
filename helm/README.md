# Deploying the Helm chart in a local Kubernetes setup

Follow these instruction to deploy the Helm chart on a local Kubernetes setup, for example Docker Desktop.

## Configure

Before deploying the helm chart you need to fill in the `DATABASE_USERNAME`, `DATABASE_PASSWORD` and `LDAP_LOOKUP_USER_PASSWORD` fields in [deploy-ci.yml](deploy-ci.yml). The values need to be base64-encoded. The default database username and password are both 'root', so set the database fields to 'cm9vdA=='. The default LDAP lookup user password is 'admin', so set the `LDAP_LOOKUP_USER_PASSWORD` to 'YWRtaW4K'.

## Deploy Helm chart

To deploy the Helm chart make sure the Kubernetes cluster is up and then run:

```console
helm install quality-time helm
```

Or run `upgrade` if you have installed the Helm chart before:

```console
helm upgrade quality-time helm
```

## Set up port-forwarding

Finally, enable port-forwarding on the proxy pod to make Quality-time reachable: 

```console
kubectl port-forward quality-time-www-pod-suffix 8080:8080
```

If you don't have tab completion working for kubectl you can find out the pod-suffix using:

```console
kubectl get pods | grep quality-time-www
```
