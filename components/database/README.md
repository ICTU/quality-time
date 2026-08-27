# *Quality-time* database

See the [software documentation](https://quality-time.readthedocs.io/en/latest/software.html#database).

## Container hardening

The `Dockerfile` starts from the official `mongo` image and then hardens it to reduce the attack surface. The
MongoDB base image lags behind the Ubuntu security updates and ships tooling that *Quality-time* does not use, so the
`RUN` instruction removes what is unneeded, upgrades what is outdated, and adjusts file ownership so the container can
run as a non-root user. This section documents each modification, why it is safe, and — for the upgrades — the guard
that fails the build once the base image makes the workaround redundant, signalling that it can be removed.

### Removals

The removals are not guarded: `apt-get purge` reports a package that is not installed and still exits successfully,
and `rm -rf` does the same for a path that is already gone, so if a future base image stops shipping one of them, the
build keeps working and the removal quietly becomes a no-op.

- **MongoDB database tools** (`mongodb-database-tools`, `mongodb-org-database-tools-extra`: `mongodump`,
  `mongorestore`, `mongoexport`, `mongostat`, etc.). Not used by the server, by *Quality-time* (the components connect
  via PyMongo), or for backups (which use a separate `mongo` container, see the deployment documentation), and they
  ship with their own vulnerabilities. The server (`mongod`) and the shell (`mongosh`, needed by the entrypoint to
  create the root user) are kept.
- **`gosu`.** The data directories are made group-owned by the root group (GID 0) and group-writable so the container
  can run as an arbitrary non-root user (some platforms, such as OpenShift, assign a random high UID with GID 0).
  Combined with running as non-root, this means `gosu` is no longer needed.
- **`ncurses-bin`.** Ships only terminal command-line tools (`tic`, `infocmp`, `tput`, `clear`, `reset`), none of which
  are needed by `mongod` or `mongosh` (verified) and nothing installed depends on it. It carries
  [CVE-2025-69720](https://www.cve.org/CVERecord?id=CVE-2025-69720), a stack-based buffer overflow in `analyze_string`
  in `progs/infocmp.c`, i.e. in the `infocmp` binary itself, so removing the package deletes the vulnerable code rather
  than merely upgrading it. `--allow-remove-essential` is required because `ncurses-bin` is marked essential; that is
  safe here because the container never installs packages at runtime. Its sibling packages from the same `ncurses`
  source — `ncurses-base` (terminfo data) and the shared libraries `libtinfo6` and `libncursesw6` (needed by `bash`,
  `procps`, and `util-linux`) — cannot all be removed and do not contain the flawed `infocmp` code, so they are
  *upgraded* rather than removed for the same CVE; see "Library upgrades".
- **`gzip`.** Ships the `gzip`, `gunzip`, `zcat`, and `gzexe` command-line tools. Not used by `mongod` (which links its
  own compression libraries), by `mongosh`, or by the entrypoint (verified), and nothing installed depends on it. It
  carries [CVE-2026-41991](https://www.cve.org/CVERecord?id=CVE-2026-41991) (arbitrary file overwrite via insecure
  temporary files in `gzexe`) and [CVE-2026-41992](https://www.cve.org/CVERecord?id=CVE-2026-41992) (buffer overflow in
  the LZH decoder), both in the `gzip` binaries themselves, so removing the package deletes the vulnerable code rather
  than merely upgrading it. `--allow-remove-essential` is required because `gzip` is marked essential; that is safe here
  because the container never installs packages at runtime.
- **`js-yaml`** (`/opt/js-yaml`, and the `/js-yaml.js` symlink pointing into it). The base image vendors the
  `dist/js-yaml.js` browser bundle of js-yaml 3.13.1 — not an apt package, but a tarball it fetches from the npm
  registry — so that `docker-entrypoint.sh` can turn a YAML config file into JSON before starting `mongod`. That code
  runs on one path only, `--config <file>`, which *Quality-time* never takes: the compose file starts the
  container with `--quiet` and the Helm chart sets no `command` or `args`. The vendored copy carries
  [GHSA-5p4m-2wfm-xmqj](https://github.com/advisories/GHSA-5p4m-2wfm-xmqj), quadratic CPU consumption while resolving
  `!!omap`, whose upstream fix (CVE-2026-59870) was never backported to the 3.13.x series; it is fixed in 3.15.1 and
  4.3.1. Deleting the bundle removes the vulnerable code rather than upgrading it, and avoids having to vendor and
  checksum a replacement tarball ourselves. The trade-off is that this image no longer accepts `--config`: the
  entrypoint then reports `error: unexpected "js-yaml.js" output while parsing config` and exits non-zero, so
  configure `mongod` with command-line flags instead.

### Library upgrades

Three packages are upgraded to pull in Ubuntu security fixes the base image does not ship yet.

**`openssl` and `libssl3t64`** are upgraded to `3.0.13-0ubuntu3.15`, from
[USN-8678-1](https://ubuntu.com/security/notices/USN-8678-1). Trivy flags the image on
[CVE-2026-63076](https://www.cve.org/CVERecord?id=CVE-2026-63076), an invalid pointer dereference in the CMP server
reached via a crafted `protectionAlg`; the same package version also fixes
[CVE-2026-54874](https://www.cve.org/CVERecord?id=CVE-2026-54874) (DTLS),
[CVE-2026-63072](https://www.cve.org/CVERecord?id=CVE-2026-63072) (CMS key unwrapping),
[CVE-2026-63074](https://www.cve.org/CVERecord?id=CVE-2026-63074) (CMP certificate cache), and
[CVE-2026-75803](https://www.cve.org/CVERecord?id=CVE-2026-75803) (AEAD tag verification). The remaining CVEs in that
notice affect Ubuntu 26.04 only, not the Noble base image.

**`libcurl4t64`** is upgraded to `8.5.0-2ubuntu10.13`. Trivy flags the image on
[CVE-2026-11856](https://www.cve.org/CVERecord?id=CVE-2026-11856) — libcurl reuses a handle's `Authorization:` header
across a change of origin, leaking `hostA`'s Digest credentials to `hostB` — which Ubuntu fixed one patch earlier, in
`8.5.0-2ubuntu10.12` ([USN-8651-1](https://ubuntu.com/security/notices/USN-8651-1)). The guard is deliberately pinned
to `.13` rather than to that fix version, because `--only-upgrade` installs the current Noble candidate either way,
and `.13` ([USN-8670-1](https://ubuntu.com/security/notices/USN-8670-1)) additionally fixes
[CVE-2026-8932](https://www.cve.org/CVERecord?id=CVE-2026-8932), connection reuse that ignores changed client
certificate settings. Pinning the guard to `.12` would announce the upgrade as redundant while `.13` was still needed.
Only the library is installed here — the `curl` command-line package is not in the base image — and `libcurl4t64` is
required by `mongodb-org-server`, so it is upgraded rather than removed.

None of these are reachable from *Quality-time*: `mongod` uses OpenSSL for TLS and never acts as a CMP or CMS
endpoint, and it does not drive libcurl through Digest-authenticated transfers or client-certificate handle reuse.
They are upgraded anyway, because the fix is a package upgrade rather than a code change, and a published image that
ships a package version with a known fix available is reported by every downstream scan.

Each package is paired with a minimum version in a guard that fails the build — naming the package — once the base
image ships that version or newer, or stops shipping the package at all. That is what signals the manual upgrade can
be dropped again; bump the version in the guard whenever a newer fix has to be pulled in. The guard checks the whole
list in one pass and fails only after reporting all of it, so a single build shows every entry that has become
redundant rather than one per rebuild. Once the list is empty, drop the guard, the `apt-get install --only-upgrade`
step, and the linter exception below along with it.

The `package=min-version` list is the single source of truth for both halves of the step. The loop splits each entry
on `=` to compare the minimum against what is installed, and appends the package name to the shell's positional
parameters, so the install can pass a quoted `"$@"` instead of word-splitting an accumulated string. Keeping it
quoted is what lets the step pass ShellCheck's SC2086 and SonarQube's S6570 without a suppression in either tool; add
new packages to that one list and nothing else needs touching.

`ncurses-base`, `libtinfo6`, and `libncursesw6` are left as the base image ships them, even though their sibling
`ncurses-bin` is removed for [CVE-2025-69720](https://www.cve.org/CVERecord?id=CVE-2025-69720). The vulnerable code
lives only in the `infocmp` binary shipped by `ncurses-bin`; these three packages contain terminfo data
(`ncurses-base`) and shared library code (`libtinfo6`, `libncursesw6`) that do not include the flawed function, so
Trivy flags them purely on the shared `ncurses` source version. They cannot simply be dropped either — `libtinfo6` and
`libncursesw6` are required by `bash`, `procps`, and `util-linux`, and `ncurses-base` provides the terminfo that
`mongosh` and `bash` use for interactive terminal rendering. The base image now ships the fixed `ncurses` version, so
these findings are clear without a manual upgrade.

### Linter exceptions

- **DL3008** (pin apt versions) is intentionally ignored: `--only-upgrade` pulls the latest security patch rather than
  a fixed version, and the guard above bounds the minimum. It is the only ignore the `Dockerfile` carries.

### Runtime user

The container runs as the non-root MongoDB user (UID 999) by default. Platforms that require a UID >= 1000 can override
this with a `securityContext` (see the deployment documentation); the data directories are group-writable for GID 0.
