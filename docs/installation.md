# Installation

The CLI requires Python 3.11 or newer and the 1Password desktop app.

## Install as a standalone command

The recommended installation uses `uv`:

```sh
uv tool install op-find-item
```

Alternatively, install with `pipx`:

```sh
pipx install op-find-item
```

You can also install it into the active Python environment with `pip`:

```sh
python -m pip install op-find-item
```

Confirm installation:

```sh
op-find-item --help
```

## Install from source

Clone the [GitHub repository](https://github.com/sbfeinstein/op-find-item), then install the project and its development dependencies:

```sh
git clone https://github.com/sbfeinstein/op-find-item.git
cd op-find-item
uv sync
```

Run the CLI from the checkout with:

```sh
uv run op-find-item --help
```
