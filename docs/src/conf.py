"""Configuration file for the Sphinx documentation builder."""

# pylint: disable=invalid-name
# pragma: no cover

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("."))

# Build reference manual with overview of subjects, metrics, and sources.
import create_reference_md  # pylint: disable=wrong-import-position

create_reference_md.main()

# -- Project information -----------------------------------------------------

project = "Quality-time"
copyright = "2021-2023, ICTU"  # pylint: disable=redefined-builtin
author = "ICTU"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["myst_parser", "sphinx_copybutton", "sphinx_design", "sphinx.ext.graphviz"]
myst_enable_extensions = ["colon_fence", "deflist"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# exclude_patterns = []

# -- Options for MyST parser -------------------------------------------------

# See https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#auto-generated-header-anchors
myst_heading_anchors = 3

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_logo = "_static/Quality-time.png"
html_title = "Quality-time"
html_favicon = "../../components/frontend/public/favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for linkcheck ---------------------------------------------------

linkcheck_ignore = [
    r"http://localhost",  # Getting started URL
    r"http://localhost:\d+",  # Example URLs
    "http://quality-time.example.org",  # Example URLs
    # False negative: Anchor 'recognized-languages-' not found:
    "https://github.com/AlDanial/cloc#recognized-languages-",
    # False negative: Anchor 'api-name-axerun' not found
    "https://github.com/dequelabs/axe-core/blob/develop/doc/API.md#api-name-axerun",
    "https://trello.com/1/members/me/boards",  # Only works when logged in
    # False negative: Anchor 'results-object' not found"
    "https://github.com/dequelabs/axe-core/blob/develop/doc/API.md#results-object",
    "https://react.semantic-ui.com/collections/table/#states",  # False negative: Anchor 'states' not found
]
