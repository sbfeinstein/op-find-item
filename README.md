# 1Password Find Item

![PyPI version](https://img.shields.io/pypi/v/op-find-item.svg)

`op-find-item` is an (unofficial) tool to find 1Password items containing a given search term.

**This is an independent piece of software** and is not connected to or sanctioned
by [1Password](https://1password.com/) or AgileBits Inc.

* GitHub: https://github.com/sbfeinstein/op-find-item/
* PyPI package: https://pypi.org/project/op-find-item/
* Created by: **Scott Feinstein** | GitHub https://github.com/sbfeinstein | PyPI https://pypi.org/user/sfeinstein/
* Free software: [MIT LICENSE](LICENSE)

## Features

* Search your 1Password items for a search term
* Secure. Requires authentication through the 1Password desktop application
* Supports case-sensitive or case-insensitive searches
* Supports limiting search to particular Vaults and item fields
* Outputs in human-readable mode by default, with progress bars
* Supports JSON as an alternative output format
* Leverages 1Password's official [SDK](https://developer.1password.com/docs/sdks/) for all operations

## Documentation site

`op-find-item`'s documentation is built with [Zensical](https://zensical.org/) and published to GitHub Pages.

* **Live site:** https://sbfeinstein.github.io/op-find-item/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

Docs deploy automatically on releases (not simply pushes to `main`) via GitHub Actions.

Docs may also be manually deployed to GitHub Pages via `just docs-publish`.

## Development

Create a fork in GitHub if you intend to contribute (see [Contributing](CONTRIBUTING.md)).
Or directly clone the `op-find-item` if you just want to build and play with the project.

To set up for local development:

```bash
# Locally clone https://github.com/sbfeinstein/op-find-item.git or your fork:
git clone git@github.com:your_username/op-find-item.git
cd op-find-item

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available
when you run `op-find-item`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## DevOps setup and configuration

This project has several external dependencies related to how it is built, published and distributed. This all refers
to how the project is distributed; all execution of the tool itself is local with no communication to any servers
of any sort, for any reason.

The build, etc., dependencies are:

* GitHub for:
    * The source code repository
    * CI/CD via GitHub Actions
    * Hosting the static documentation site (GitHub Pages)
* PyPI for distribution

Regarding PyPI, this workflow requests a short-lived OIDC identity only in its PyPI publish job.
This approach removes the need for a PyPI API token or GitHub Actions secrets in support of publishing to PyPI.

See PyPI's
[Trusted Publishers guide](https://docs.pypi.org/trusted-publishers/) and the
[PyPA GitHub Actions publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/).

Supporting the above required these configuration changes, which were performed manually:

* Configure the repo to publish to Pages,
  see [Creating a GitHub Pages Site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
    * Manually build and publish a `gh-pages` branch by running `just docs-publish`
    * Make sure the [Pages](https://github.com/sbfeinstein/tunic-language-tool/settings/pages) settings are:
        * Source "Deploy from a branch"
        * Branch "gh-pages" "/(root)"
        * "Enforce HTTPS" is checked
    * After an initial manual publishing of the docs, in the `github-pages` Environment that gets created, add "v*" tags as an allowed entry under "Deployment branches and tags".  This allows the release workflow to publish updated documentation.
* Configure PyPI to support being published to from GitHub Actions
    * In PyPI account or project publishing settings, add a Trusted Publisher for
      owner `sbfeinstein`, repository `op-find-item`, workflow filename
      `publish.yml`, and GitHub Environment `pypi`. For a project not yet created
      on PyPI, add a pending publisher in the account's publishing settings.
    * In GitHub repository settings, create the `pypi` environment, restrict
      deployments to `v*` release tags, and require a reviewer to approve
      deployments.

## Author

1Password Find Item was created in 2026 by Scott Feinstein.

## Software scaffold

The code for this project was scaffolded using [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and
the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
