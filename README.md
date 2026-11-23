# 1Password Find Item

![PyPI version](https://img.shields.io/pypi/v/op-find-item.svg)

`op-find-item` is an (unofficial) tool to find 1Password items containing a given search term.

**This is an independent piece of software** and is not connected to or sanctioned by [1Password](https://1password.com/) or AgileBits Inc.

* GitHub: https://github.com/sbfeinstein/op-find-item/
* PyPI package: https://pypi.org/project/op-find-item/
* Created by: **Scott Feinstein** | GitHub https://github.com/sbfeinstein | PyPI https://pypi.org/user/sfeinstein/
* Free software: MIT License

## Features

* Search your 1Password items for a search term
* Secure.  Requires authentication through the 1Password desktop application
* Supports case-sensitive or case-insensitive searches
* Supports limiting search to particular Vaults and item fields
* Outputs in human-readable mode by default, with progress bars
* Supports JSON as an alternative output format
* Leverages 1Password's official [SDK](https://developer.1password.com/docs/sdks/) for all operations

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://sbfeinstein.github.io/op_find_item/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

Create a fork in GitHub if you intend to contribute (see [Contributing](CONTRIBUTING.md)).
Or directly clone the `op_find_item` if you just want to build and play with the project.

To set up for local development:

```bash
# Locally clone https://github.com/sbfeinstein/op-find-item.git or your fork:
git clone git@github.com:your_username/op-find-item.git
cd op-find-item

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `op-find-item`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

1Password Find Item was created in 2026 by Scott Feinstein.

## Scaffold

This project was scaffolded using [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
