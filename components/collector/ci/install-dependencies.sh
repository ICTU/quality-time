#!/bin/bash

uv sync --locked --extra dev
uv pip install -e ../shared_code
