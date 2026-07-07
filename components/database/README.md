# *Quality-time* database

See the [software documentation](https://quality-time.readthedocs.io/en/latest/software.html#database).

## Container hardening

The `Dockerfile` starts from the official `mongo` image and then hardens it to reduce the attack surface. The
MongoDB base image lags behind the Ubuntu security updates and ships tooling that *Quality-time* does not use, so the
`RUN` instruction removes what is unneeded, upgrades what is outdated, and adjusts file ownership so the container can
run as a non-root user. This section documents each modification, why it is safe, and — where applicable — the guard
that fails the build once the base image makes the workaround redundant, signalling that it can be removed.

### Removals

- **MongoDB database tools** (`mongodb-database-tools`, `mongodb-org-database-tools-extra`: `mongodump`,
  `mongorestore`, `mongoexport`, `mongostat`, etc.). Not used by the server, by *Quality-time* (the components connect
  via PyMongo), or for backups (which use a separate `mongo` container, see the deployment documentation), and they
  ship with their own vulnerabilities. The server (`mongod`) and the shell (`mongosh`, needed by the entrypoint to
  create the root user) are kept.
- **`gosu`.** The data directories are made group-owned by the root group (GID 0) and group-writable so the container
  can run as an arbitrary non-root user (some platforms, such as OpenShift, assign a random high UID with GID 0).
  Combined with running as non-root, this means `gosu` is no longer needed.
- **`js-yaml` 3.13.1** (`/opt/js-yaml`, symlinked as `/js-yaml.js`). Bundled by the base image solely so the entrypoint
  can parse a `mongod` YAML config passed via `--config`. *Quality-time* never passes `--config` (see
  `docker-compose.yml` and the Helm chart), so this parser is unreachable here, yet it carries
  [CVE-2025-64718](https://www.cve.org/CVERecord?id=CVE-2025-64718) (prototype pollution). A guard fails the build if
  the base image stops shipping `js-yaml` at this path, signalling that this cleanup can be removed.
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

### Library upgrades

Several libraries are upgraded to pick up the latest Ubuntu security fixes ahead of the base image. Each package is
paired with a minimum version in a guard that fails the build once the base image itself ships that version or newer,
signalling that the manual upgrade can be removed; bump the version in a guard whenever a newer fix needs to be pulled
in.

`ncurses-base`, `libtinfo6`, and `libncursesw6` are upgraded here (not removed) for
[CVE-2025-69720](https://www.cve.org/CVERecord?id=CVE-2025-69720), even though their sibling `ncurses-bin` is removed
for that same CVE. The vulnerable code lives only in the `infocmp` binary shipped by `ncurses-bin`; these three
packages contain terminfo data (`ncurses-base`) and shared library code (`libtinfo6`, `libncursesw6`) that do not
include the flawed function, so Trivy flags them purely on the shared `ncurses` source version. They cannot simply be
dropped — `libtinfo6` and `libncursesw6` are required by `bash`, `procps`, and `util-linux`, and `ncurses-base`
provides the terminfo that `mongosh` and `bash` use for interactive terminal rendering — so upgrading to the fixed
version is the way to clear these findings.

### Linter exceptions

- **DL3008** (pin apt versions) is intentionally ignored: `--only-upgrade` pulls the latest security patch rather than a
  fixed version, and the guards above bound the minimum.
- **SC2086** is ignored for the deliberate word-split of "package min-version" pairs in the upgrade loop.

### Runtime user

The container runs as the non-root MongoDB user (UID 999) by default. Platforms that require a UID >= 1000 can override
this with a `securityContext` (see the deployment documentation); the data directories are group-writable for GID 0.
