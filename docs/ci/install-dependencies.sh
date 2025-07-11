#!/bin/bash

npm install --ignore-scripts
uv sync --active --locked --extra dev  # Add --active so the prepared virtual env is used on ReadTheDocs
