#!/bin/sh

pip install --user selenium
python -m unittest discover --start-directory tests
