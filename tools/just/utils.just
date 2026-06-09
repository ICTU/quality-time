exists(path) := path_exists(invocation_directory() + "/" + path)

# === Python/uv/pyproject.toml ===

pyproject_toml_exists := exists("pyproject.toml")
pyproject_toml_contents := if pyproject_toml_exists == "true" { read(invocation_directory() + "/pyproject.toml") } else { "" }
has_py_pkg(name) := if pyproject_toml_contents =~ f'"{{name}}[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }

uv_run := "uv run --quiet"
uv_run_project_wide_tool := uv_run + " --project " + justfile_directory() + "/tools/third_party"
python := uv_run + " python"

# === JavaScript/npm/package.json ===

package_json_exists := exists("package.json")
js_scripts := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts") } else { "{}" }
has_js_script(name) := if js_scripts =~ f'"{{name}}"' { "true" } else { "false" }

npm_run := "npm run --silent"

# === Folders ===

at_root := if invocation_directory() == justfile_directory() { "true" } else { "false" }
# The current folder relative to the repo root (empty at the root); used by `ci` to label its output.
current_folder := if at_root == "true" { "" } else { replace(invocation_directory(), justfile_directory() + "/", "") }
src_folder := if exists("src") == "true" { "src" } else { "" }
tests_folder := if exists("tests") == "true" { "tests" } else { "" }
code := if trim(src_folder + " " + tests_folder) == "" { ".?*.py" } else { src_folder + " " + tests_folder }
components := `ls components`

# === Output functions ===

# Prefix and suffix that wrap a command (such as a check): `{{ start_capture(folder) }} <cmd> {{ end_capture(name) }}` captures stdout+stderr, prints `<recipe-name> [<folder>/ ]OK` or `NOK`, and replays the captured output on failure.
folder_prefix(folder) := if folder == "" { "" } else if folder == "." { "" } else { " " + trim_end_match(folder, "/") + "/" }

# Pick a tool-flag value based on `$_color` set by `start_capture`. Useful for tools whose color flag values aren't `auto`/`always`/`never` (e.g. bandit's `screen`/`txt`, yamllint's `colored`/`auto`).
when_color(yes, no) := f'$([ "$_color" = always ] && echo {{yes}} || echo {{no}})'

start_capture(folder) := f'_color=auto; [ -t 1 ] && { _color=always; export FORCE_COLOR=1; }; f="{{folder_prefix(folder)}}"; output=$({'
end_capture(name) := f'; } 2>&1) || { printf "%s%s {{RED}}NOK{{NORMAL}}\n%s\n" {{name}} "$f" "$output"; exit 1; }; printf "%s%s {{GREEN}}OK{{NORMAL}}\n" {{name}} "$f"'

# Like start_capture/end_capture, but for slow commands (e.g. tests): run them in the background and animate a spinner while they run. The spinner only shows for an unlabelled run on a terminal (a direct, interactive `just test`); labelled runs (a parallel `ci` or fan-out) skip it, so it never smears into their atomic OK/NOK lines.
start_progress(folder) := f'f="{{folder_prefix(folder)}}"; if [ -t 1 ] && [ -z "$f" ]; then spin=1; else spin=; fi; tmp=$(mktemp); trap "rm -f $tmp" EXIT; { '
end_progress(name) := f'; } > "$tmp" 2>&1 & pid=$!; sp="|/-\\"; while kill -0 "$pid" 2>/dev/null; do [ -n "$spin" ] && printf "\r%c" "$sp"; sp="${sp#?}${sp%???}"; sleep 0.1; done; [ -n "$spin" ] && printf "\r"; wait "$pid" && printf "%s%s {{GREEN}}OK{{NORMAL}}\n" {{name}} "$f" || { printf "%s%s {{RED}}NOK{{NORMAL}}\n%s\n" {{name}} "$f" "$(cat "$tmp")"; exit 1; }'

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
