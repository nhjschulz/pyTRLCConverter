# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyTRLCConverter'
copyright = '2025, NewTec GmbH'
author = 'NewTec GmbH'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # https://www.sphinx-doc.org/en/master/usage/markdown.html
    'myst_parser',

    # https://github.com/sphinx-contrib/plantuml
    'sphinxcontrib.plantuml'
]

templates_path = ['_templates']
exclude_patterns = []

# Support restructured text and Markdown
source_suffix = ['.rst', '.md']

# -- MyST parser configuration ---------------------------------------------------

# Configure MyST parser to generate GitHub-style anchors
myst_heading_anchors = 3

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'haiku'
html_static_path = ['_static']

# Copy favorite icon to static path.
html_favicon = '../../../doc/images/favicon.ico'

# Copy logo to static path.
html_logo = '../../../doc/images/NewTec_Logo.png'

# PlantUML is called OS depended and the java jar file is provided by environment variable.
plantuml = ['java', '-jar', os.getenv('PLANTUML')]
