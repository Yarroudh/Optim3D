import os
import sys
import datetime
sys.path.insert(0, os.path.abspath('../../'))

project = 'Optim3D'
copyright = '2023, Anass Yarroudh'
author = 'Anass Yarroudh'
version = '0.1.9'
author_website = 'http://geomatics.ulg.ac.be/'
company = 'Geomatics Unit of ULiège'
github_url = 'https://github.com/Yarroudh/Optim3D'
show_powered_by = False

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_click.ext',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_context = {
    "display_github": True,
    "company": "Geomatics Unit of ULiège",
    "website": "https://github.com/Yarroudh/Optim3D",
    "footer": "Copyright © {} {} | {}"
              .format(datetime.datetime.now().year, "Geomatics Unit of University of Liège", "All rights reserved."),
    'display_version': True,
    'versions': ['latest'],
    'current_version': 'latest',
    'version_dropdown': True,
}

html_show_sphinx = False

html_context = {
    
}

html_context = {
    'display_github': True,
    'github_user': 'yarroudh',
    'github_repo': 'Optim3D',
    'github_version': 'main/docs/',
}