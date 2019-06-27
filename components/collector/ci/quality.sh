#!/bin/sh

mypy src
pylint src
safety check --bare -r requirements.txt -r requirements-dev.txt
