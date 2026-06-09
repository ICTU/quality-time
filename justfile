set guards
set positional-arguments
set quiet
set unstable # for user-defined functions

_default:
    @just --list

# List all recipes, or show usage (options and arguments) for one recipe, e.g. `just help test`.
help recipe="":
    @if [ -z "{{ recipe }}" ]; then just --list; \
    else just --usage {{ recipe }}; \
    if just --show {{ recipe }}-help > /dev/null 2>&1; then just {{ recipe }}-help; fi; fi

export COVERAGE_RCFILE := justfile_directory() + "/.coveragerc"
components := `ls components`
exists(path) := path_exists(invocation_directory() + "/" + path)
docker_folder_exists := exists("docker")
package_json_exists := exists("package.json")
pyproject_toml_exists := exists("pyproject.toml")
pyproject_toml_contents := if pyproject_toml_exists == "true" { read(invocation_directory() + "/pyproject.toml") } else { "" }
js_scripts := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts") } else { "{}" }
has_js_script(name) := if js_scripts =~ f'"{{name}}"' { "true" } else { "false" }
has_py_pkg(name) := if pyproject_toml_contents =~ f'"{{name}}[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
has_py_unit_tests := if pyproject_toml_exists == "true" { exists("tests") } else { "false" }
at_root := if invocation_directory() == justfile_directory() { "true" } else { "false" }
# The current folder relative to the repo root (empty at the root); used by `ci` to label its output.
current_folder := if at_root == "true" { "" } else { replace(invocation_directory(), justfile_directory() + "/", "") }
src_folder := if exists("src") == "true" { "src" } else { "" }
tests_folder := if exists("tests") == "true" { "tests" } else { "" }
code := if trim(src_folder + " " + tests_folder) == "" { ".?*.py" } else { src_folder + " " + tests_folder }
uv_run := "uv run --quiet"
python := uv_run + " python"
coverage := uv_run + " coverage"
fixit := uv_run + " fixit --quiet"
just_fmt := "just --unstable --fmt"
pyproject_fmt := uv_run + " pyproject-fmt --no-generate-python-version-classifiers"
ruff := uv_run + " ruff --quiet"
troml := uv_run + " troml"
ty := uv_run + ' ty check --no-progress --error-on-warning --color=${_color:-auto}'
vulture := uv_run + " vulture --exclude .venv --min-confidence 0"
vulture_whitelist := ".vulture-whitelist.py"
sphinx_build := uv_run + " sphinx-build"
npm_run := "npm run --silent"
project_wide_tools := uv_run + " --project " + justfile_directory() + "/tools/third_party"
# Prefix and suffix that wrap a command (such as a check): `{{ start_capture(folder) }} <cmd> {{ end_capture(name) }}` captures stdout+stderr, prints `<recipe-name> [<folder>/ ]OK` or `NOK`, and replays the captured output on failure.
folder_prefix(folder) := if folder == "" { "" } else if folder == "." { "" } else { " " + trim_end_match(folder, "/") + "/" }
# Pick a tool-flag value based on `$_color` set by `start_capture`. Useful for tools whose color flag values aren't `auto`/`always`/`never` (e.g. bandit's `screen`/`txt`, yamllint's `colored`/`auto`).
when_color(yes, no) := f'$([ "$_color" = always ] && echo {{yes}} || echo {{no}})'
start_capture(folder) := f'_color=auto; [ -t 1 ] && { _color=always; export FORCE_COLOR=1; }; f="{{folder_prefix(folder)}}"; output=$({'
end_capture(name) := f'; } 2>&1) || { printf "%s%s {{RED}}NOK{{NORMAL}}\n%s\n" {{name}} "$f" "$output"; exit 1; }; printf "%s%s {{GREEN}}OK{{NORMAL}}\n" {{name}} "$f"'
# Like start_capture/end_capture, but for slow commands (e.g. tests): run them in the background and animate a spinner while they run. The spinner only shows for an unlabelled run on a terminal (a direct, interactive `just test`); labelled runs (a parallel `ci` or fan-out) skip it, so it never smears into their atomic OK/NOK lines.
start_progress(folder) := f'f="{{folder_prefix(folder)}}"; if [ -t 1 ] && [ -z "$f" ]; then spin=1; else spin=; fi; tmp=$(mktemp); trap "rm -f $tmp" EXIT; { '
end_progress(name) := f'; } > "$tmp" 2>&1 & pid=$!; sp="|/-\\"; while kill -0 "$pid" 2>/dev/null; do [ -n "$spin" ] && printf "\r%c" "$sp"; sp="${sp#?}${sp%???}"; sleep 0.1; done; [ -n "$spin" ] && printf "\r"; wait "$pid" && printf "%s%s {{GREEN}}OK{{NORMAL}}\n" {{name}} "$f" || { printf "%s%s {{RED}}NOK{{NORMAL}}\n%s\n" {{name}} "$f" "$(cat "$tmp")"; exit 1; }'
pid_filename := "/tmp/quality-time-" + file_name(invocation_directory()) + "-pid.txt"
# Run a started component in the background (detach) or foreground, recording its PID either way.
record_pid(mode) := if mode == "detach" { "& echo $! > " + pid_filename } else { "; echo $! > " + pid_filename }
# Terminal width is read at parse time from stderr (still a TTY when stdout is captured by $() ); falls back to 200 if there's no TTY (CI, piped output).
term_width := shell(f"{{project_wide_tools}} python -c 'import os; print(os.get_terminal_size(2).columns if os.isatty(2) else 200)'")

# === Update dependencies ===

# Update dependencies of type.
[private]
update dependency_type:
    {{ uv_run }} --project tools/update_dependencies tools/update_dependencies/src/update_{{ dependency_type }}.py

# Update direct and indirect dependencies. Set GITHUB_TOKEN, DOCKER_HUB_USERNAME, and DOCKER_HUB_TOKEN to prevent hitting rate limits.
[parallel]
update-dependencies: (update "dockerfile_base_image") (update "pyproject_toml") (update "github_action") (update "circle_ci_config") (update "docker_compose") (update "jsdelivr")
    # node_engine and package_json both rewrite the package.json files, so they run sequentially here (not as parallel dependencies) to avoid concurrent writes to the same files.
    just update "node_engine"
    just update "package_json"

alias update-deps := update-dependencies

# === Install dependencies ===

# Install Python dependencies from the lock file.
[no-cd]
[private]
install-py-dependencies:
    ?[ {{ pyproject_toml_exists }} = true ]
    uv sync --no-progress --quiet --locked --all-extras --all-groups --reinstall-package shared-code --reinstall-package shared-test-code

# Install JavaScript dependencies from the lock file.
[no-cd]
[private]
install-js-dependencies:
    ?[ {{ package_json_exists }} = true ]
    ?[ ! -e node_modules/.package-lock.json ] || [ package-lock.json -nt node_modules/.package-lock.json ]
    npm ci --silent

# === Lock dependencies ===

# Update the Python lock file(s). Run `just help lock` for more information.
[arg("scope", long="all", short="a", value="all", help="Update lock files in all relevant folders, not just the current folder")]
[no-cd]
lock scope="":
    {{ if scope == "all" { "just lock-all" } else if exists("uv.lock") == "true" { "just lock-in-folder" } else { 'echo "No lock file to update in this folder"' } }}

# Update the Python lock file in the current folder.
[no-cd]
[private]
lock-in-folder:
    ?[ {{ exists("uv.lock") }} = true ]
    uv lock

# Update all Python lockfiles. Folders without a lock file are skipped by lock-in-folder's guard above.
[private]
lock-all: (for-each folders_to_check "run lock-in-folder")

# === Build artifacts ===

# Build the docker containers.
[no-cd]
[private]
build-docker *components:
    ?[ {{ docker_folder_exists }} = true ]
    docker compose build {{ components }}

# Build the JavaScript artifact(s) from the code.
[no-cd]
[private]
build-js: install-js-dependencies
    ?[ {{ has_js_script("build") }} = true ]
    {{ npm_run }} build

# Build the documentation from the code.
[no-cd]
[private]
build-docs: install-py-dependencies
    ?[ {{ has_py_pkg("sphinx") }} = true ]
    {{ sphinx_build }} -W --keep-going src build

# Build artifacts in the current folder. Run `just help build` for more information.
[no-cd]
build *components:
    just build-in-folder {{ components }}

# Build the artifacts or components.
[no-cd]
[private]
build-in-folder *components: build-docs build-js (build-docker components)
    ?[ {{ has_py_pkg("sphinx") }} = false ] && [ {{ has_js_script("build") }} = false ] && [ {{ docker_folder_exists }} = false ]
    echo "Nothing to build in this folder"

# Show extended help for the build recipe.
[private]
build-help:
    echo
    echo {{ BOLD }}{{ YELLOW }}'What `build` does in each folder:'{{ NORMAL }}
    echo - In docs/, builds the documentation.
    echo - In components/frontend/, builds the frontend bundle.
    echo - In the project root, builds Docker components. Pass one or more component names
    echo "  to build specific Docker components or no names to build them all."
    echo "  Possible Docker component names are:"
    echo '  {{ CYAN }}{{ replace(components, "\n", ", ") }}'{{ NORMAL }}

# === Start and stop components ===

# Start the Docker containers.
[no-cd]
[private]
start-docker-component mode *components:
    ?[ {{ docker_folder_exists }} = true ]
    COLUMNS=$({{ python }} -c 'import subprocess; s = subprocess.run(["docker", "compose", "config", "--services"], capture_output=True, text=True).stdout; print({{ term_width }} - max(len(line.strip()) for line in s.splitlines()) - 6)') docker compose up {{ if mode == "detach" { "--detach" } else { "" } }} {{ components }}

# Start the Python component.
[no-cd]
[private]
start-py-component mode="attach": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ python }} src/quality_time*.py {{ record_pid(mode) }}

# Start the JavaScript component.
[no-cd]
[private]
start-js-component mode="attach": install-js-dependencies
    ?[ {{ has_js_script("start") }} = true ]
    {{ npm_run }} start {{ record_pid(mode) }}

# Start the component(s) in the current folder. Run `just help start` for more information.
[arg("mode", long="detach", short="d", value="detach", help="Run components in the background")]
[no-cd]
start mode="attach" *components:
    just start-in-folder {{ mode }} {{ components }}

# Start the component(s) in the current folder, if possible.
[no-cd]
[private]
start-in-folder mode="attach" *components: (start-py-component mode) (start-js-component mode) (start-docker-component mode components)
    ?[ {{ pyproject_toml_exists }} = false ] && [ {{ has_js_script("start") }} = false ] && [ {{ docker_folder_exists }} = false ]
    echo "Nothing to start in this folder"

# Show extended help for the start recipe.
[private]
start-help:
    echo
    echo {{ BOLD }}{{ YELLOW }}'What `start` does in each folder:'{{ NORMAL }}
    echo - In components/api_server/, starts the API-server locally.
    echo - In components/collector/, starts the collector locally.
    echo - In components/notifier/, starts the notifier locally.
    echo - In components/frontend/, starts the frontend locally.
    echo - In the project root, starts Docker components. Pass one or more component names
    echo '  to start specific Docker components or no names to start them all.'
    echo '  Possible Docker component names are:'
    echo '  {{ CYAN }}{{ replace(components, "\n", ", ") }}'{{ NORMAL }}

# Stop the locally started component, if any.
[no-cd]
[private]
stop-component:
    ?[ {{ path_exists(pid_filename) }} = true ]
    kill $(cat {{ pid_filename }})
    rm {{ pid_filename }}

# Stop one or more Docker components
[no-cd]
[private]
stop-docker-components *components:
    ?[ {{ docker_folder_exists }} = true ]
    docker compose stop {{ components }}

# Stop the component(s) in the current folder.
stop *components: stop-component (stop-docker-components components)
    ?[ {{ pyproject_toml_exists }} = false ] && [ {{ has_js_script("start") }} = false ] && [ {{ docker_folder_exists }} = false ]
    echo "Nothing to stop in this folder"

# === Run tests ===

# Run the Python unit tests. Pass '--coverage=no' to skip reporting test coverage.
[arg("cov", long="coverage", short="c", pattern="default|yes|no", help="Measure unit test coverage?")]
[env("PYTHONDEVMODE", "1")]
[env("PYTHONPATH", "src")]
[no-cd]
[private]
py-unit-test cov="yes" folder="" *tests: install-py-dependencies
    ?[ {{ has_py_unit_tests }} = true ]
    # Show a spinner while running; suppress output unless the run fails; with coverage, also write the reports (xml fails if coverage is too low, but only after the text and HTML reports have been generated).
    {{ start_progress(folder) }} {{ if cov == "no" { python } else { coverage + " run" } }} -m unittest --quiet {{ tests }}{{ if cov != "no" { " && " + coverage + " report --fail-under=0 && " + coverage + " html --quiet --fail-under=0 && " + coverage + " xml --quiet" } else { "" } }} {{ end_progress("py-unit-test") }}

# Run the JavaScript unit tests. Pass '--coverage=yes' to measure test coverage. Without explicit tests or coverage, only the tests for uncommitted changes are run if there are any.
[arg("cov", long="coverage", short="c", pattern="default|yes|no", help="Measure unit test coverage?")]
[no-cd]
[private]
js-unit-test cov="no" folder="" *tests: install-js-dependencies
    ?[ {{ has_js_script("test") }} = true ]
    # Show a spinner while running; suppress output unless the tests fail. Without explicit tests or coverage, only run the tests for uncommitted changes, if any.
    {{ start_progress(folder) }} if [ "{{ cov }}" = "yes" ]; then args="--coverage"; \
    elif [ -n "{{ tests }}" ]; then args="{{ tests }}"; \
    elif ! git diff --quiet HEAD -- {{ invocation_directory() }}/src; then args="--changed"; \
    else args=""; fi; \
    {{ npm_run }} test -- $args {{ end_progress("js-unit-test") }}

[no-cd]
[private]
test-in-folder cov="default" folder="" *tests: (py-unit-test cov folder tests) (js-unit-test cov folder tests)
    ?[ {{ has_py_unit_tests }} = false ] && [ {{ has_js_script("test") }} = false ]
    echo "Nothing to test in this folder"

# Run the unit tests. Run `just help test` for more information.
[arg("cov", long="coverage", short="c", pattern="default|yes|no", help="Measure unit test coverage? Default means yes for Python and no for Javascript")]
[arg("scope", long="all", short="a", value="all", help="Run tests in all relevant folders")]
[no-cd]
test cov="default" scope="" *tests:
    {{ if scope == "all" { "just test-all" } else { "just test-in-folder " + cov + " '' " + tests } }}

# Show extended help for the test recipe.
[private]
test-help:
    echo
    echo {{ BOLD }}{{ YELLOW }}'What `test` does:'{{ NORMAL }}
    echo - Without arguments, runs the unit tests in the current folder.
    echo "  (cd into a component or docs folder first, or use {{ GREEN }}-a, --all{{ NORMAL }} for all relevant folders)."
    echo - Pass test names or paths as positional arguments to run only those tests.
    echo "- Coverage defaults to on for Python and off for JavaScript; override with {{ GREEN }}--coverage yes|no{{ NORMAL }}."
    echo "  For JavaScript, without tests or coverage given, only tests for uncommitted changes run."

# Generate a JUnit XML test report at build/unittests.xml. Re-runs Python tests via xmlrunner; used by CI to feed test results to SonarCloud.
[env("PYTHONDEVMODE", "1")]
[env("PYTHONPATH", "src")]
[no-cd]
[private]
junit-xml: install-py-dependencies
    ?[ {{ has_py_unit_tests }} = true ]
    mkdir -p build
    {{ start_capture(current_folder) }} {{ uv_run }} --with=unittest-xml-reporting -m xmlrunner --output-file build/unittests.xml {{ end_capture("junit-xml") }}

# Folders with unit tests, run by `test-all`.
test_folders := "components/api_server components/collector components/frontend components/notifier components/renderer components/shared_code docs tools/release tools/update_dependencies"

# Change into the folder and run the tests there (passing the folder so the OK/NOK output is labelled with it).
[no-cd]
[private]
cd-to-folder-and-test folder: (run f"test-in-folder default {{folder}}" folder)

# Run the unit tests, in all relevant folders.
[private]
test-all: (for-each test_folders "cd-to-folder-and-test")

# === Run checks ===

# Run a Python check.
[no-cd]
[private]
py-check name check folder="": install-py-dependencies
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
pip-audit folder="": install-py-dependencies
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
vale folder="": install-py-dependencies
    ?[ {{ has_py_pkg("vale") }} = true ]
    {{ start_capture(folder) }} {{ uv_run }} vale sync && {{ uv_run }} vale --no-wrap --glob '*.md' src {{ end_capture("vale") }}

# Run a JavaScript check.
[no-cd]
[private]
js-check name check folder="": install-js-dependencies
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
npm-outdated folder="": install-js-dependencies
    ?[ {{ package_json_exists }} = true ]
    {{ start_capture(folder) }} npm outdated --json | {{ python }} -c "import json, sys; updates = [f'{k}: {v['current']} -> {v['wanted']}' for k, v in json.loads(sys.stdin.read()).items() if v['wanted'] != v['current']]; print('\n'.join(updates), end='\n' if updates else ''); sys.exit(1 if updates else 0)" {{ end_capture("npm-outdated") }}

# Run yamllint to lint YAML files such as workflow definitions.
[no-cd]
[private]
yamllint folder="":
    ?[ {{ at_root }} = true ]
    {{ start_capture(folder) }} {{ project_wide_tools }} yamllint -c .yamllint -f {{ when_color("colored", "auto") }} . {{ end_capture("yamllint") }}

# Run zizmor to audit GitHub Action workflows.
[no-cd]
[private]
zizmor folder="":
    ?[ {{ at_root }} = true ]
    {{ start_capture(folder) }} {{ project_wide_tools }} zizmor --no-progress --quiet .github/workflows {{ end_capture("zizmor") }}

# Run compose-lint on docker-compose.yml and on the merged dev and CI configurations.
[no-cd]
[private]
compose-lint folder="":
    ?[ {{ at_root }} = true ]
    tmp=$(mktemp -d); trap "rm -rf $tmp" EXIT; \
    {{ start_capture(folder) }} docker compose --file docker/docker-compose.yml --file docker/docker-compose.override.yml config --no-interpolate > $tmp/dev.yml && \
    docker compose --file docker/docker-compose.yml --file docker/docker-compose.ci.yml config --no-interpolate > $tmp/ci.yml && \
    {{ project_wide_tools }} compose-lint --config docker/.compose-lint.yml --fail-on low --skip-suppressed docker/docker-compose.yml $tmp/dev.yml $tmp/ci.yml {{ end_capture("compose-lint") }}

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
    {{ project_wide_tools }} zizmor --no-progress --quiet --fix=all .github/workflows

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

# === Development modes ===

# The component folders that run as local processes in the development scenarios.
app_folders := "components/api_server components/collector components/notifier components/frontend"
# The same components as bare names, for use as Docker service names.
app_components := replace(app_folders, "components/", "")

# Start every component in Docker (scenario 1 in the developer manual).
start-docker: (for-each app_folders "run stop")
    just start -d

[private]
start-hybrid-start: (start-docker-component "detach" "database" "ldap" "renderer" "mongo-express" "testdata") (for-each app_folders 'run "start -d"')

# Start a combination of Docker services and local processes for development (scenario 2 in the developer manual).
start-hybrid: (stop-docker-components app_components)
    just start-hybrid-start

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

# === CI/CD ===

# Run all tests and checks in CI. Meant for running tests and checks in GitHub Actions and CircleCI.
# Calls the workers directly (not the `test`/`check` dispatchers) with the folder label, so the parallel output is labelled and readable and the interactive test spinner is suppressed.
[no-cd]
[parallel]
[private]
ci: (test-in-folder "yes" current_folder) (check-in-folder current_folder) junit-xml

# === Clean ===

# Clean caches, build folders, and generated files.
clean:
    rm -f .coverage */.coverage */*/.coverage
    rm -rf build */build */*/build
    rm -rf .*_cache */.*_cache */*/.*_cache
    rm -rf */node_modules */*/node_modules
    rm -rf */*.egg-info */*/*.egg-info */*/*/*.egg-info
    rm -rf */.venv */*/.venv
    rm -rf */*/dist
    rm -rf */*/htmlcov

# === Utility recipes ===

# Run the recipe in the folder.
[private]
[working-directory(folder)]
run recipe folder:
    just {{ recipe }}

# Run the recipe for each whitespace-separated item, in parallel.
[private]
for-each items recipe:
    echo {{ items }} | xargs --max-args=1 --max-procs=0 just {{ recipe }}
