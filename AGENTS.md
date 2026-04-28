# Agents

## Common tasks

Read the justfile to discover how to invoke common tasks just as running tests and checks. Note that many recipes are private to not overwhelm human users of the justfile. 

Python unit tests run with coverage by default, but it's possible to turn coverage off. Note that the test recipe has an optional variadic argument to run specific tests or testfiles.

## Commit messages

Use a short, imperative subject line describing the change. Add a body with more detail if needed. Reference the GitHub issue with `Fixes #NNNN.` or `Closes #NNNN.` in the body (not the subject — GitHub adds the PR number to the subject on merge). Example:

```
Fix collector unit test failing during DST transitions

Fixes #12868.
```
