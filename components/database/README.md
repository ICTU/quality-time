# *Quality-time* database

See the [software documentation](https://quality-time.readthedocs.io/en/latest/software.html#database).

## Container hardening

The `Dockerfile` starts from the official `mongo` image and then hardens it to reduce the attack surface. The
MongoDB base image ships tooling that *Quality-time* does not use, so the `RUN` instruction removes what is unneeded
and adjusts file ownership so the container can run as a non-root user. This section documents each modification and
why it is safe, and — under "Library upgrades" — what to do when the base image lags behind an Ubuntu security fix.

### Removals

The removals are not guarded: `apt-get purge` reports a package that is not installed and still exits successfully, so
if a future base image stops shipping one of them, the build keeps working and the removal quietly becomes a no-op.

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

### Library upgrades

No libraries are upgraded at the moment: the base image ships the Ubuntu security fixes *Quality-time* needs. It has
not always been so, and may not stay so. When the base image lags behind a fix that has to be pulled in, add the
package back to an `apt-get install --only-upgrade` step, and pair it with a minimum version in a guard that fails the
build — naming the package — once the base image ships that version or newer, or stops shipping the package at all.
That is what signals the manual upgrade can be dropped again. Check the whole list in one pass and fail only after
reporting all of it, so a single build shows every entry that has become redundant rather than one per rebuild. See
the git history of the `Dockerfile` for the previous implementation, which was removed once the base image caught up.

`ncurses-base`, `libtinfo6`, and `libncursesw6` are left as the base image ships them, even though their sibling
`ncurses-bin` is removed for [CVE-2025-69720](https://www.cve.org/CVERecord?id=CVE-2025-69720). The vulnerable code
lives only in the `infocmp` binary shipped by `ncurses-bin`; these three packages contain terminfo data
(`ncurses-base`) and shared library code (`libtinfo6`, `libncursesw6`) that do not include the flawed function, so
Trivy flags them purely on the shared `ncurses` source version. They cannot simply be dropped either — `libtinfo6` and
`libncursesw6` are required by `bash`, `procps`, and `util-linux`, and `ncurses-base` provides the terminfo that
`mongosh` and `bash` use for interactive terminal rendering. The base image now ships the fixed `ncurses` version, so
these findings are clear without a manual upgrade.

### Runtime user

The container runs as the non-root MongoDB user (UID 999) by default. Platforms that require a UID >= 1000 can override
this with a `securityContext` (see the deployment documentation); the data directories are group-writable for GID 0.
