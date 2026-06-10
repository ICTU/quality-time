set guards
set positional-arguments
set quiet
set unstable # for user-defined functions

import 'tools/just/build.just'
import 'tools/just/check.just'
import 'tools/just/ci.just'
import 'tools/just/clean.just'
import 'tools/just/dependencies.just'
import 'tools/just/deploy.just'
import 'tools/just/release.just'
import 'tools/just/test.just'
import 'tools/just/utils.just'

_default:
    @just --list

# List all recipes, or show usage (options and arguments) for one recipe, e.g. `just help test`.
help recipe="":
    @if [ -z "{{ recipe }}" ]; then just --list; \
    else just --usage {{ recipe }}; \
    if just --show {{ recipe }}-help > /dev/null 2>&1; then just {{ recipe }}-help; fi; fi

export COVERAGE_RCFILE := justfile_directory() + "/.coveragerc"
# Enable uv's malware check on every sync (it can't be enabled via pyproject.toml). The experimental-feature
# warning is suppressed by the --quiet flag on `uv sync`. See https://astral.sh/blog/uv-audit.
export UV_MALWARE_CHECK := "1"
