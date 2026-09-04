# *Quality-time* database

See the [software documentation](https://quality-time.readthedocs.io/en/latest/software.html#database).

## Container hardening

The `Dockerfile` starts from the official `mongo` image and hardens it in one `RUN` instruction: it purges tooling
*Quality-time* does not use, upgrades packages for which Ubuntu has shipped security fixes that the base image does not
carry yet, and makes the data directories group-writable so the container can run as a non-root user. This section is
the maintenance guide for that instruction.

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

Twenty-three packages are upgraded to pull in Ubuntu security fixes the base image does not ship yet. The list covers
every package for which Trivy reports a fixed version, so that a scan of the built image comes back empty; add a row
whenever a scan turns up a new one. Each package is paired with a minimum version in the `Dockerfile`'s
`package=min-version` list; the Ubuntu notice lists the CVEs each one fixes. The table is ordered as the list is, so
the two can be compared line by line.

| Package(s) | Minimum version | Ubuntu notice | Upgraded rather than removed because |
| --- | --- | --- | --- |
| `bsdutils`, `libblkid1`, `libmount1`, `libsmartcols1`, `libuuid1`, `mount`, `util-linux` | `2.39.3-9ubuntu6.6`, and `bsdutils` carries epoch `1:` | [USN-8702-1](https://ubuntu.com/security/notices/USN-8702-1) | `util-linux` and `bsdutils` are essential; the libraries are required by `util-linux`, `mount`, and `e2fsprogs` |
| `coreutils` | `9.4-3ubuntu6.3` | [USN-8697-1](https://ubuntu.com/security/notices/USN-8697-1) | essential |
| `diffutils` | `1:3.10-1ubuntu0.1` | [USN-8692-1](https://ubuntu.com/security/notices/USN-8692-1) | essential, and `dpkg` requires `/usr/bin/diff`: purging it makes the very next `dpkg --configure` fail with "expected program not found in PATH", so the purge step above cannot complete. Verified — do not retry |
| `gpgv` | `2.4.4-2ubuntu17.6` | [USN-8720-1](https://ubuntu.com/security/notices/USN-8720-1) | required by `apt` |
| `libattr1` | `1:2.5.2-1ubuntu0.1` | [USN-8691-1](https://ubuntu.com/security/notices/USN-8691-1) | required by `coreutils` |
| `libbz2-1.0` | `1.0.8-5.1ubuntu0.1` | [USN-8685-1](https://ubuntu.com/security/notices/USN-8685-1) | required by `dpkg`, `gpgv`, and `libsemanage2` |
| `libcurl4t64` | `8.5.0-2ubuntu10.13` | [USN-8670-1](https://ubuntu.com/security/notices/USN-8670-1) | required by `mongodb-org-server` |
| `libgcrypt20` | `1.10.3-2ubuntu0.2` | [USN-8711-1](https://ubuntu.com/security/notices/USN-8711-1) | required by `gpgv`, `libapt-pkg6.0t64`, and `libsystemd0` |
| `libncursesw6`, `libtinfo6`, `ncurses-base` | `6.4+20240113-1ubuntu2.2` | [USN-8709-1](https://ubuntu.com/security/notices/USN-8709-1) | `ncurses-base` is essential and holds the terminfo `mongosh` and `bash` use; `libtinfo6` is required by `bash`, `procps`, and `util-linux`, and `libncursesw6` by `procps`. Their sibling `ncurses-bin` is removed instead, see above |
| `libp11-kit0` | `0.25.3-4ubuntu2.2` | [USN-8687-1](https://ubuntu.com/security/notices/USN-8687-1) | dependency of `libgnutls30t64` |
| `libssh-4` | `0.10.6-2ubuntu0.5` | [USN-8699-1](https://ubuntu.com/security/notices/USN-8699-1) | required by `libcurl4t64` |
| `libssl3t64`, `openssl` | `3.0.13-0ubuntu3.15` | [USN-8678-1](https://ubuntu.com/security/notices/USN-8678-1) | `mongod` uses OpenSSL for TLS |
| `perl-base` | `5.38.2-3.2ubuntu0.4` | [USN-8684-1](https://ubuntu.com/security/notices/USN-8684-1) | `apt` and `dpkg` run Perl scripts (the `debconf` frontend, `dpkg-reconfigure`) while performing the purges above |
| `zlib1g` | `1:1.3.dfsg-3.1ubuntu2.2` | [USN-8706-1](https://ubuntu.com/security/notices/USN-8706-1) | required by `dpkg`, `libapt-pkg6.0t64`, `libcurl4t64`, `libssh-4`, and `util-linux` |

Three things are worth knowing when reading Trivy's output against this list:

- Trivy matches on the *source* version, so one notice yields a finding per binary package, and it reports a package
  whose source is vulnerable even when the vulnerable binary is not installed. `gpgv` ships only `/usr/bin/gpgv`, not
  the `gpgsm` its CVE is in; `libbz2-1.0` and `libattr1` ship libraries only, not the `bzip2recover` and
  `getfattr`/`setfattr` their CVEs are in. They are upgraded regardless, because the fix is a package upgrade.
- The `libcurl4t64` guard is pinned to `.13` rather than to `.12`, the version that fixed the CVE Trivy reports
  ([USN-8651-1](https://ubuntu.com/security/notices/USN-8651-1)): `--only-upgrade` installs the current Noble
  candidate either way, and `.13` fixes a further CVE, so pinning to `.12` would announce the upgrade as redundant
  while `.13` was still needed.
- None of these are on a code path *Quality-time* exercises. They are upgraded anyway, because a published image that
  ships a package version with a known fix available is reported by every downstream scan.

**Maintaining the list.** The guard fails the build — naming the package — once the base image ships the minimum
version or newer, or stops shipping the package at all; that is the signal to drop the entry. It checks the whole list
in one pass and reports every redundant entry before failing, so one build shows all of them. Bump a minimum version
whenever a newer fix has to be pulled in. Once the list is empty, drop the guard, the `apt-get install --only-upgrade`
step, and the DL3008 exception below along with it.

The `package=min-version` list is the single source of truth for both halves of the step: the loop splits each entry on
`=` to compare the minimum against what is installed, and appends the package name to the shell's positional
parameters so the install can pass a quoted `"$@"` instead of word-splitting an accumulated string. Keeping it quoted
is what lets the step pass ShellCheck's SC2086 and SonarQube's S6570 without a suppression in either tool. Add new
packages to that one list and nothing else needs touching.

### Linter exceptions

**DL3008** (pin apt versions) is ignored because `--only-upgrade` pulls the latest security patch rather than a fixed
version, and the guard bounds the minimum. It is the only ignore the `Dockerfile` carries.

### Runtime user

The container runs as the non-root MongoDB user (UID 999) by default. Platforms that require a UID >= 1000 can override
this with a `securityContext` (see the deployment documentation); the data directories are group-writable for GID 0.
