"""Virtual environments: a private copy of Python per project, so packages
don't clash between projects. This project uses `uv` (uv sync, uv run,
uv add) instead of the stdlib venv + pip. This file inspects the interpreter
it's running under so an activated environment's effect is visible."""

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
