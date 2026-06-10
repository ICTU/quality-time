import 'dependencies.just'

coverage := uv_run + " coverage"
has_py_unit_tests := if pyproject_toml_exists == "true" { exists("tests") } else { "false" }

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
