"""Virtual environments.

A virtual environment is a private copy of Python for one project, so each
project can install its own packages and versions without clashing.

Creating one with the standard library tool:

    python -m venv .venv           create it
    source .venv/bin/activate      use it (Linux/macOS)
    pip install fastapi            installs into .venv, not the system Python
    pip freeze > requirements.txt  record what is installed
    deactivate                     leave it

This project is managed with `uv`, which creates the environment and resolves
dependencies from pyproject.toml in one step:

    uv sync                        create .venv and install everything
    uv run python topics/10_virtual_environments.py
    uv add pypdf                   add a dependency and update uv.lock

This file just inspects the interpreter it is running under so the effect of
an activated environment is visible.
"""

from __future__ import annotations

import sys
from importlib import metadata


def in_virtual_environment() -> bool:
    # Inside a venv, sys.prefix (this environment) differs from
    # sys.base_prefix (the Python it was created from).
    return sys.prefix != sys.base_prefix


def main() -> None:
    print("interpreter :", sys.executable)
    print("version     :", sys.version.split()[0])
    print("sys.prefix  :", sys.prefix)
    print("base_prefix :", sys.base_prefix)
    print("in a venv?  :", in_virtual_environment())

    packages = sorted(
        (dist.metadata["Name"], dist.version) for dist in metadata.distributions()
    )
    print(f"\ninstalled packages ({len(packages)}):")
    for name, version in packages:
        print(f"  {name}=={version}")


if __name__ == "__main__":
    main()
