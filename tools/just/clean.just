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
