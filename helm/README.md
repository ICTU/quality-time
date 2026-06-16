# Deploying the Helm chart in a local Kubernetes setup

Follow these instruction to deploy the Helm chart on a local Kubernetes setup, for example Docker Desktop.

## Configure

Before deploying the helm chart you need to fill in the `DATABASE_USERNAME`, `DATABASE_PASSWORD` and `LDAP_LOOKUP_USER_PASSWORD` fields in [deploy-ci.yml](deploy-ci.yml).
The values need to be base64-encoded. The default database username and password are both 'root', so set the database fields to 'cm9vdA=='.
The default LDAP lookup user password is 'admin', so set the `LDAP_LOOKUP_USER_PASSWORD` to 'YWRtaW4K'.

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

## Customizing

The chart sets a `securityContext` on each component (and, for the database, also a `podSecurityContext`), including `readOnlyRootFilesystem: true`. Helm deep-merges your overrides onto these defaults, so you only need to specify the keys you want to change; the other defaults stay in place. To *remove* a default key, set it to `null` in your override — omitting it leaves the default unchanged. Note that lists, such as `capabilities.drop`, are replaced rather than merged when you override them.

### Running the database as a different user

By default the database container runs as the `mongodb` user (UID 999). Some platforms (such as OpenShift) require containers to run with a UID >= 1000 or assign an arbitrary high UID. The database image supports this: its data directories (`/data/db` and `/data/configdb`) are group-owned by the root group (GID 0) and group-writable, so the container can run as any non-root user that belongs to GID 0.

To run the database as a fixed UID >= 1000, override the user in the `securityContext` and set a matching `fsGroup` in the `podSecurityContext` so the platform makes the persistent volume writable for that user:

```yaml
database:
  securityContext:
    capabilities:
      drop:
        - ALL
    readOnlyRootFilesystem: true
    runAsUser: 1000 # any value >= 1000
    runAsGroup: 0
  podSecurityContext:
    fsGroup: 1000
    fsGroupChangePolicy: OnRootMismatch
```

### Running the database with an arbitrary UID (OpenShift)

On platforms that assign an arbitrary UID (such as OpenShift with the default `restricted-v2` SCC), don't pin the UID or group at all: the platform picks the UID, runs it with GID 0, and the data directories are already group-writable for GID 0. Because the chart ships `runAsUser: 999`, `runAsGroup: 999`, `fsGroup: 999`, and `fsGroupChangePolicy` as defaults, and Helm keeps unspecified defaults, you have to *remove* all four by setting them to `null`:

```yaml
database:
  securityContext:
    capabilities:
      drop:
        - ALL
    readOnlyRootFilesystem: true
    runAsUser: null
    runAsGroup: null
  podSecurityContext:
    fsGroup: null
    fsGroupChangePolicy: null
```

This leaves only `capabilities` and `readOnlyRootFilesystem` in the `securityContext` and an empty `podSecurityContext`. OpenShift then injects the UID and, via its `MustRunAs` `fsGroup` strategy, an allowed `fsGroup` of its own. Hardcoding `runAsUser` or `fsGroup` to a value outside the namespace's allowed range would get the pod rejected, which is why they are removed rather than set.

### Migrating an existing deployment

When changing the UID of an *existing* deployment, the data files are owned by UID 999, so an `fsGroup` must be set to let the platform re-own the volume's group on mount; otherwise the new user cannot read the existing data. On a fixed-UID platform, set `fsGroup` to the new UID (as in the example above). On OpenShift, set it to a value within the namespace's allowed range (see the namespace's `openshift.io/sa.scc.supplemental-groups` annotation) rather than letting it default, and not to `999`. Fresh installs are not affected.
