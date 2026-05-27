# ╔══════════════════════════════════════════════════════════════════╗
# ║  Umbral — conf                                                   ║
# ║  « module »                                                      ║
# ╠══════════════════════════════════════════════════════════════════╣
# ╚══════════════════════════════════════════════════════════════════╝


"""Sphinx configuration."""
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "Umbral"
author = "Jenkins, Cahill-Lane & Geurten"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
html_theme = "furo"
autodoc_mock_imports = []
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
