import 'utils.just'

# === Release ===

# Release Quality-time. Run `just help release` for more information.
[working-directory('tools/release')]
release *args:
    {{ uv_run }} --script src/release.py {{ args }}

# Show the release script's own help, dropping its `usage:` line (the usage is already printed by `help` via `just --usage release`). Force color so the captured help stays colored; strip the first line with shell parameter expansion to avoid an external tool.
[private]
release-help:
    @export FORCE_COLOR=1; \
    nl=$(printf '\nx'); nl=${nl%x}; \
    help=$(just release --help); \
    printf '%s\n' "${help#*"$nl"}"
