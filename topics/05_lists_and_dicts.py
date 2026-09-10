"""Lists and dictionaries in more depth.

Covers list comprehensions and common dictionary methods.
"""


def main() -> None:
    numbers = [3, 8, 1, 9, 4, 7, 2]

    # List methods
    numbers.sort()
    print("sorted:", numbers)
    print("max/min/sum:", max(numbers), min(numbers), sum(numbers))
    print("sliced:", numbers[1:4])

    # List comprehension: [expression for item in iterable if condition]
    squares = [n * n for n in numbers]
    evens = [n for n in numbers if n % 2 == 0]
    print("squares:", squares)
    print("evens:", evens)

    # Dictionary basics
    week = {
        "number": 21,
        "topic": "embeddings and vector databases",
        "project": "Document Indexer",
    }

    # .get() returns a default instead of raising KeyError
    print(week.get("number"))
    print(week.get("missing", "not set"))

    # Iterating a dict
    for key, value in week.items():
        print(f"{key}: {value}")

    print("keys:", list(week.keys()))
    print("values:", list(week.values()))

    # Updating and removing
    week["done"] = True
    week.update({"topic": "vector search"})
    removed = week.pop("done")
    print("removed:", removed, "->", week)

    # Dict comprehension: count word lengths
    words = ["chunk", "embed", "store", "retrieve"]
    lengths = {word: len(word) for word in words}
    print(lengths)

    # Grouping data with a dict
    scores = [("math", 70), ("math", 80), ("cs", 90), ("cs", 60)]
    grouped: dict[str, list[int]] = {}
    for subject, score in scores:
        grouped.setdefault(subject, []).append(score)
    print(grouped)


if __name__ == "__main__":
    main()
