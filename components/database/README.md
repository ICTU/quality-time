# *Quality-time* database

See the [software documentation](https://quality-time.readthedocs.io/en/latest/software.html#database).

## Container hardening

The `Dockerfile` starts from the official `mongo` image and hardens it in one `RUN` instruction: it purges tooling
*Quality-time* does not use and makes the data directories group-writable so the container can run as a non-root user.
This section is the maintenance guide for that instruction.

### Removals

Removals are deliberately unguarded: `apt-get purge` succeeds on a package that is not installed and `rm -rf` on a path
that is already gone, so a removal silently becomes a no-op once the base image stops shipping its target. Removing a
package deletes the vulnerable code outright, so it is preferred over upgrading whenever nothing needs the package.

- **`mongodb-database-tools` and `mongodb-org-database-tools-extra`** (`mongodump`, `mongorestore`, `mongoexport`,
  `mongostat`, and so on). The components connect via PyMongo and backups use a separate `mongo` container (see the
  deployment documentation), so only `mongod` and `mongosh` — needed by the entrypoint to create the root user — are
  kept. Purging these also removes the `mongodb-org-database` and `mongodb-org-tools` metapackages that depend on them.
- **`ncurses-bin`**, for [CVE-2025-69720](https://www.cve.org/CVERecord?id=CVE-2025-69720), which is in the `infocmp`
  binary itself. It ships terminal tools only (`tic`, `infocmp`, `tput`, `clear`, `reset`), nothing installed depends
  on it, and `mongod` and `mongosh` do not need it.
- **`gzip`**, for [CVE-2026-41991](https://www.cve.org/CVERecord?id=CVE-2026-41991) and
  [CVE-2026-41992](https://www.cve.org/CVERecord?id=CVE-2026-41992), both in the `gzip` binaries themselves. `mongod`
  links its own compression libraries, and nothing installed depends on the package.
- **`/usr/local/bin/gosu`**, made redundant by running as a non-root user with data directories owned by the root
  group (GID 0) and group-writable, which also lets the container run as the arbitrary high UID that platforms such as
  OpenShift assign.
- **`/opt/js-yaml` and the `/js-yaml.js` symlink**, for
  [GHSA-5p4m-2wfm-xmqj](https://github.com/advisories/GHSA-5p4m-2wfm-xmqj), which was never backported to the vendored
  js-yaml 3.13.1 browser bundle. The entrypoint uses the bundle only for `mongod --config <file>`, a path neither the
  compose file (it passes `--quiet`) nor the Helm chart (it sets no `command` or `args`) takes.

`ncurses-bin` and `gzip` are marked essential, hence `--allow-remove-essential`; that is safe because the container
never installs packages at runtime.

**Trade-off:** the image no longer accepts `mongod --config <file>`. The entrypoint reports
`error: unexpected "js-yaml.js" output while parsing config` and exits non-zero, so configure `mongod` with
command-line flags instead.

### Library upgrades

There are none, and the step needs no network access as a result: the base image ships every Ubuntu security fix Trivy
knows a fixed version for, so a scan of the built image comes back empty without upgrading anything.

That was not always so. The `Dockerfile` used to upgrade twenty-three packages that could not be removed because
something installed needs them, each pinned to a `package=min-version` guard that failed the build once the base image
caught up. As of the `mongo:8.3.9` base image all twenty-three guards fired at once, so the guard, the
`apt-get install --only-upgrade` step, and the `apt-get update` that fed it were dropped. Two things learned there are
worth keeping:

- Trivy matches on the *source* version, so one Ubuntu notice yields a finding per binary package, and it reports a
  package whose source is vulnerable even when the vulnerable binary is not installed. `gpgv` ships only
  `/usr/bin/gpgv`, not the `gpgsm` its CVE was in; `libbz2-1.0` and `libattr1` ship libraries only, not the
  `bzip2recover` and `getfattr`/`setfattr` theirs were in. Such findings still need the package upgraded, because a
  package upgrade is the only fix on offer.
- `diffutils` cannot be purged even though it is only needed at build time: `dpkg` requires `/usr/bin/diff`, so the
  very next `dpkg --configure` fails with "expected program not found in PATH" and the purges above cannot complete.
  Verified — do not retry.

**When a scan reports a new vulnerability.** Prefer bumping the base image; the `mongo` image usually picks up Ubuntu
security fixes within days. Purge the package if nothing installed depends on it (see *Removals*). Only if neither
works, reintroduce an upgrade step: `apt-get --option Acquire::Retries=3 update` followed by
`apt-get --option Acquire::Retries=3 install --only-upgrade --yes --no-install-recommends <package>`, a
`hadolint ignore=DL3008` because `--only-upgrade` pulls the latest patch rather than a pinned version, and a guard that
fails the build once the base image makes the upgrade redundant. The retries matter because the base image configures
none, and CI builds this image in four workflows in parallel, so a single `archive.ubuntu.com` hiccup — a 503, a reset
connection, a hash sum mismatch — would abort the build with apt's exit code 100 and not reproduce.

### Runtime user

The container runs as the non-root MongoDB user (UID 999) by default. Platforms that require a UID >= 1000 can override
this with a `securityContext` (see the deployment documentation); the data directories are group-writable for GID 0.
