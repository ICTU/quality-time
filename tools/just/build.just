import 'dependencies.just'

docker_folder_exists := exists("docker")
sphinx_build := uv_run + " sphinx-build"

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
