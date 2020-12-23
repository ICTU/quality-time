#!/bin/sh

pip install --progress-bar off --user selenium
python -m unittest discover --start-directory tests/application_tests
