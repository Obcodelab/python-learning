"""File handling with context managers.

`with open(...)` closes the file automatically, even if an error happens.
This file writes a sample document, reads it back, then cleans up.
"""

from pathlib import Path


def main() -> None:
    path = Path(__file__).parent / "sample_output.txt"

    lines = [
        "Week 20 - file handling",
        "Reading and writing text files",
        "Using context managers",
        "Processing content line by line",
    ]

    # Writing
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    # Reading the whole file
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print("full content:\n", content)

    # Reading line by line (like processing a document)
    with open(path, "r", encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            print(f"{number}: {line.rstrip()}")

    # pathlib has shortcuts for small files
    print("word count:", len(path.read_text(encoding="utf-8").split()))

    # Appending
    with open(path, "a", encoding="utf-8") as f:
        f.write("One more line\n")
    print("line count after append:", len(path.read_text().splitlines()))

    # Clean up so the topics folder stays tidy
    path.unlink()
    print("cleaned up:", not path.exists())


if __name__ == "__main__":
    main()
