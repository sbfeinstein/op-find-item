"""Smoke test an installed distribution's package and console entry point."""

import subprocess
from importlib.metadata import version


def main() -> None:
    version("op-find-item")
    subprocess.run(["op-find-item", "--help"], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    main()
