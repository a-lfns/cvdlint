from importlib.metadata import version

project = "cvdlint"
author = "Alice Alfonsi"
copyright = "2026, Alice Alfonsi"
release = version("cvdlint")
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

autodoc_typehints = "description"
html_theme = "furo"
html_title = f"cvdlint {release}"
html_logo = "assets/cvdlint-lockup-dark.svg"
html_favicon = "assets/cvdlint-logo.svg"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-brand-primary": "#5D3A9B",
        "color-brand-content": "#5D3A9B",
        "color-brand-visited": "#5D3A9B",
        "color-highlight-on-target": "rgba(230, 97, 0, 0.16)",
    },
    "dark_css_variables": {
        "color-brand-primary": "#9B79D0",
        "color-brand-content": "#9B79D0",
        "color-brand-visited": "#9B79D0",
        "color-highlight-on-target": "rgba(230, 97, 0, 0.16)",
    },
    "source_repository": "https://github.com/a-lfns/cvdlint/",
    "source_branch": "main",
    "source_directory": "docs/",
}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
