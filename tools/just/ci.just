import 'check.just'
import 'test.just'

# === CI/CD ===

# Run all tests and checks in CI. Meant for running tests and checks in GitHub Actions and CircleCI.
# Calls the workers directly (not the `test`/`check` dispatchers) with the folder label, so the parallel output is labelled and readable and the interactive test spinner is suppressed.
[no-cd]
[parallel]
[private]
ci: (test-in-folder "yes" current_folder) (check-in-folder current_folder) junit-xml
