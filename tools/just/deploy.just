import 'build.just'

pid_filename := "/tmp/quality-time-" + file_name(invocation_directory()) + "-pid.txt"
# Run a started component in the background (detach) or foreground, recording its PID either way.
record_pid(mode) := if mode == "detach" { "& echo $! > " + pid_filename } else { "; echo $! > " + pid_filename }
# Terminal width is read at parse time from stderr (still a TTY when stdout is captured by $() ); falls back to 200 if there's no TTY (CI, piped output).
term_width := shell(f"{{uv_run_project_wide_tool}} python -c 'import os; print(os.get_terminal_size(2).columns if os.isatty(2) else 200)'")

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
    {{ python }} src/main.py {{ record_pid(mode) }}

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
