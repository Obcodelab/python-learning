"""Modules and packages: a module is a .py file, a package is a folder of
modules, and `import` brings names in from either.

    uv run python topics/06_modules_and_packages.py"""

# 1. Import a whole standard-library module
import math

# 2. Import specific names from a module
from datetime import date

# 3. Import with an alias
import json as json_module

# 4. Import from a package (statistics is part of the standard library)
from statistics import mean, median


def main() -> None:
    print("pi:", math.pi)
    print("sqrt(144):", math.sqrt(144))

    print("today:", date.today().isoformat())

    data = {"week": 19, "topic": "modules"}
    print("json:", json_module.dumps(data))

    marks = [12, 15, 20, 9, 18]
    print("mean:", mean(marks), "median:", median(marks))

    # __name__ is "__main__" when the file is run directly,
    # and the module name when it is imported elsewhere.
    print("__name__ is:", __name__)


if __name__ == "__main__":
    main()
