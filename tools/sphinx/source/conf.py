# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import shutil

from urllib.parse import urlparse
from sphinx.errors import ConfigError

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
plantuml_env = os.getenv('PLANTUML')
plantuml = []

if plantuml_env is None:
    raise ConfigError(
        "The environment variable PLANTUML is not defined to either the location "
        "of plantuml.jar or server URL.\n"
        "Set plantuml to either <path>/plantuml.jar or a server URL.")

if  urlparse(plantuml_env).scheme in ['http', 'https']:
    plantuml = [plantuml_env]
else:
    if os.path.isfile(plantuml_env):
        plantuml = ['java', '-jar', plantuml_env]
    else:
        raise ConfigError(
            f"The environment variable PLANTUML points to a not existing file {plantuml_env}."
        )

def setup(app: any) -> None:
    """Setup sphinx.

    Args:
        app (any): The sphinx application.
    """
    app.connect('builder-inited', copy_coverage_files)

def copy_coverage_files(app: any) -> None:
    """Copy coverage files to the output directory.

    Args:
        app (any): The sphinx application.
    """
    source_dir = os.path.abspath('../createTestReport/out/coverage')
    target_dir = os.path.join(app.outdir, 'coverage')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for filename in os.listdir(source_dir):
        full_file_name = os.path.join(source_dir, filename)
        if os.path.isfile(full_file_name):
            print(f'Copy {full_file_name} to {target_dir}\n')
            shutil.copy(full_file_name, target_dir)
