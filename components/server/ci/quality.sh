#!/bin/sh

mypy src
pylint src --exit-zero
