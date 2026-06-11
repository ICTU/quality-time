import 'utils.just'

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
install-py-dependencies folder="":
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_capture(folder) }} uv sync --no-progress --locked --all-extras --all-groups --reinstall-package shared-code --reinstall-package shared-test-code {{ end_capture("install-py-dependencies") }}

# Install JavaScript dependencies from the lock file.
[no-cd]
[private]
install-js-dependencies folder="":
    ?[ {{ package_json_exists }} = true ]
    ?[ ! -e node_modules/.package-lock.json ] || [ package-lock.json -nt node_modules/.package-lock.json ]
    {{ start_capture(folder) }} npm ci {{ end_capture("install-js-dependencies") }}

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
    uv lock --quiet

# Update all Python lockfiles. Folders without a lock file are skipped by lock-in-folder's guard above.
[private]
lock-all: (for-each folders_to_check "run lock-in-folder")
