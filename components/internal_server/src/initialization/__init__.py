"""Functions to run on startup of Quality-time."""

from .bottle import init_bottle
from .migration import merge_unmerged_measurements
