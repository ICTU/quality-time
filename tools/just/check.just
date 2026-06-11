import 'build.just'

fixit := uv_run + " fixit --quiet"
just_fmt := "just --unstable --fmt"
pyproject_fmt := uv_run + " pyproject-fmt --no-generate-python-version-classifiers"
ruff := uv_run + " ruff --quiet"
troml := uv_run + " troml"
ty := uv_run + ' ty check --no-progress --error-on-warning --color=${_color:-auto}'
vulture := uv_run + " vulture --exclude .venv --min-confidence 0"
vulture_whitelist := ".vulture-whitelist.py"

# === Run checks ===

# Run a Python check.
[no-cd]
[private]
py-check name check folder="": (install-py-dependencies folder)
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_capture(folder) }} {{ check }} {{ end_capture(name) }}

# Run ty to type check Python code.
[no-cd]
[private]
ty folder="": (py-check "ty" f"{{ty}} {{code}}" folder)

# Run mypy to type check Python code.
[no-cd]
[private]
mypy folder="": (py-check "mypy" f"{{uv_run}} mypy {{code}}" folder)

# Run fixit to lint Python code.
[no-cd]
[private]
fixit folder="": (py-check "fixit" f"{{fixit}} lint {{code}}" folder)

# Run ruff to lint and check the formatting of Python code.
[no-cd]
[private]
ruff folder="": (py-check "ruff" f"{{ruff}} format --check {{code}} && {{ruff}} check {{code}}" folder)

# Run pyproject-fmt to check the formatting of pyproject.toml files.
[no-cd]
[private]
pyproject-fmt folder="": (py-check "pyproject-fmt" f"{{pyproject_fmt}} --check pyproject.toml" folder)

# Run troml to the check the classifiers in pyproject.toml files.
[no-cd]
[private]
troml folder="": (py-check "troml" f"{{troml}} check" folder)

# Run pip-audit to check Python dependencies for known security vulnerabilities.
[no-cd]
[private]
pip-audit folder="": (install-py-dependencies folder)
    ?[ {{ pyproject_toml_exists }} = true ]
    req=$(mktemp); trap "rm -f $req" EXIT; \
    {{ start_capture(folder) }} uv export --quiet --color never --directory . --format requirements-txt --no-emit-package shared-code --no-emit-package shared-test-code > $req && \
    {{ uv_run }} pip-audit --requirement $req --disable-pip --progress-spinner off {{ end_capture("pip-audit") }}

# Run uv audit to check Python dependencies for known security vulnerabilities.
[no-cd]
[private]
uv-audit folder="": (py-check "uv-audit" f"uv audit --locked --quiet" folder)

# Run bandit to check Python code for security vulnerabilities.
[no-cd]
[private]
bandit folder="": (py-check "bandit" f"{{uv_run}} bandit --configfile pyproject.toml --quiet --recursive --format {{when_color("screen", "txt")}} {{code}}" folder)

# Run vulture to check for dead Python code.
[no-cd]
[private]
vulture folder="": (py-check "vulture" f"{{vulture}} {{code}} {{vulture_whitelist}}" folder)

# Run vale to check markdown files for spelling and style.
[no-cd]
[private]
vale folder="": (install-py-dependencies folder)
    ?[ {{ has_py_pkg("vale") }} = true ]
    {{ start_capture(folder) }} {{ uv_run }} vale sync && {{ uv_run }} vale --no-wrap --glob '*.md' src {{ end_capture("vale") }}

# Run a JavaScript check.
[no-cd]
[private]
js-check name check folder="": (install-js-dependencies folder)
    ?[ {{ package_json_exists }} = true ]
    {{ start_capture(folder) }} {{ check }} {{ end_capture(name) }}

# Run npm lint to check JavaScript code.
[no-cd]
[private]
npm-lint folder="": (js-check "npm-lint" f"{{npm_run}} lint --if-present" folder)

# Run npm audit to check JavaScript dependencies for known security vulnerabilities.
[no-cd]
[private]
npm-audit folder="": (js-check "npm-audit" f"npm audit" folder)

# Run npm outdated to check for outdated JavaScript dependencies. Ignore outdated packages that can't be updated (current == wanted).
[no-cd]
[private]
npm-outdated folder="": (install-js-dependencies folder)
    ?[ {{ package_json_exists }} = true ]
    {{ start_capture(folder) }} npm outdated --json | {{ python }} -c "import json, sys; updates = [f'{k}: {v['current']} -> {v['wanted']}' for k, v in json.loads(sys.stdin.read()).items() if v['wanted'] != v['current']]; print('\n'.join(updates), end='\n' if updates else ''); sys.exit(1 if updates else 0)" {{ end_capture("npm-outdated") }}

# Run yamllint to lint YAML files such as workflow definitions.
[no-cd]
[private]
yamllint folder="":
    ?[ {{ at_root }} = true ]
    {{ start_capture(folder) }} {{ uv_run_project_wide_tool }} yamllint -c .yamllint -f {{ when_color("colored", "auto") }} . {{ end_capture("yamllint") }}

# Run zizmor to audit GitHub Action workflows.
[no-cd]
[private]
zizmor folder="":
    ?[ {{ at_root }} = true ]
    {{ start_capture(folder) }} {{ uv_run_project_wide_tool }} zizmor --no-progress --quiet .github/workflows {{ end_capture("zizmor") }}

# Run compose-lint on docker-compose.yml and on the merged dev and CI configurations.
[no-cd]
[private]
compose-lint folder="":
    ?[ {{ at_root }} = true ]
    tmp=$(mktemp -d); trap "rm -rf $tmp" EXIT; \
    {{ start_capture(folder) }} docker compose --file docker/docker-compose.yml --file docker/docker-compose.override.yml config --no-interpolate > $tmp/dev.yml && \
    docker compose --file docker/docker-compose.yml --file docker/docker-compose.ci.yml config --no-interpolate > $tmp/ci.yml && \
    {{ uv_run_project_wide_tool }} compose-lint --config docker/.compose-lint.yml --fail-on low --skip-suppressed docker/docker-compose.yml $tmp/dev.yml $tmp/ci.yml {{ end_capture("compose-lint") }}

# Check the justfile for correct formatting.
[private]
check-justfile folder="":
    ?[ {{ at_root }} = true ]
    {{ start_capture(folder) }} {{ just_fmt }} --check --color=$_color {{ end_capture("check-justfile") }}

# Run helm lint
[no-cd]
[private]
helm-lint folder="":
    ?[ {{ at_root }} = true ]
    ?[ `which helm` ]
    {{ start_capture(folder) }} helm lint --quiet --strict helm/ {{ end_capture("helm-lint") }}

# Run the quality checks in the current folder.
[no-cd]
[parallel]
[private]
check-in-folder folder="": (ty folder) (mypy folder) (fixit folder) (ruff folder) (pyproject-fmt folder) (troml folder) (pip-audit folder) (uv-audit folder) (bandit folder) (vulture folder) (vale folder) (npm-lint folder) (npm-audit folder) (npm-outdated folder) (check-justfile folder) (yamllint folder) (zizmor folder) (compose-lint folder) (helm-lint folder)

# Change into the folder and run the checks there (passing the folder so the OK/NOK output is labelled with it).
[no-cd]
[private]
cd-to-folder-and-check folder: (run f"check-in-folder {{folder}}" folder)

# Run the quality checks. Run `just help check` for more information.
[arg("scope", long="all", short="a", value="all", help="Run checks in all relevant folders")]
[no-cd]
check scope="" *folders:
    {{ if scope == "all" { "just check-all" } else if folders == "" { "just check-in-folder" } else { "just for-each \"" + folders + "\" cd-to-folder-and-check" } }}

# Show extended help for the check recipe.
[private]
check-help:
    echo
    echo {{ BOLD }}{{ YELLOW }}'What `check` does:'{{ NORMAL }}
    echo - Without arguments, runs the quality checks in the current folder.
    echo "  (cd into a component or docs folder first)."
    echo - With folder arguments, runs the checks in those folders in parallel.
    echo - With {{ GREEN }}-a, --all{{ NORMAL }}, runs the checks in all relevant folders.
    echo - These project-wide checks only run from the repo root:
    echo '  {{ CYAN }}yamllint, zizmor, compose-lint, check-justfile, helm-lint'{{ NORMAL }}

# Folders to be checked for quality.
folders_to_check := "components/api_server components/collector components/frontend components/notifier components/renderer components/shared_code docs tests/application_tests tests/feature_tests tests/shared_test_code tools/release tools/third_party tools/update_dependencies ."

# Run the quality checks, in all relevant folders.
[private]
check-all: (for-each folders_to_check "cd-to-folder-and-check")

# Run sphinx linkcheck. Excluded from `just check` because external link availability makes it flaky and slow; runs on a schedule in CI.
[no-cd]
linkcheck: install-py-dependencies
    ?[ {{ has_py_pkg("sphinx") }} = true ]
    echo Running sphinx linkcheck may take a while, be patient...
    {{ sphinx_build }} -M linkcheck src build --quiet --jobs auto

# === Fix issues ===

# Fix Python quality issues that can be fixed automatically, in the current folder.
[no-cd]
[private]
fix-py: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ ty }} --fix {{ code }}
    {{ ruff }} format {{ code }}
    {{ ruff }} check --fix {{ code }}
    {{ fixit }} fix {{ code }}
    # Pyproject-fmt returns exit code 1 when pyproject.toml needs formatting, ignore it when formatting:
    {{ pyproject_fmt }} --no-print-diff pyproject.toml || true
    {{ troml }} suggest --fix
    # Vulture returns exit code 3 when there is dead code, ignore it when writing the whitelist:
    {{ vulture }} --make-whitelist {{ code }} > {{ vulture_whitelist }} || true

# Fix zizmor issues that can be fixed automatically.
[no-cd]
[private]
fix-zizmor:
    ?[ {{ at_root }} = true ]
    {{ uv_run_project_wide_tool }} zizmor --no-progress --quiet --fix=all .github/workflows

# Fix JavaScript quality issues that can be fixed automatically, in the current folder.
[no-cd]
[private]
fix-js: install-js-dependencies
    ?[ {{ has_js_script("fix") }} = true ]
    {{ npm_run }} fix

# Fix quality issues that can be fixed automatically, in the current folder.
[no-cd]
[parallel]
fix: fix-py fix-js fix-zizmor
    {{ just_fmt }}
