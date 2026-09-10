"""Variables and the built-in data types.

Covers int, float, str, bool, and the main containers: list, tuple, dict, set.
"""


def main() -> None:
    # Numbers
    count = 42               # int
    price = 19.99            # float
    print(count / 5)         # true division -> float
    print(count // 5)        # floor division -> int
    print(count % 5)         # remainder
    print(2 ** 10)           # power

    # Strings are immutable
    title = "document q&a bot"
    print(title.title())
    print(title.replace(" ", "-"))
    print(title.split())
    print(title[:8])         # slicing

    # Booleans are a subclass of int
    print(True + True)       # 2

    # None is the "no value" object
    result = None
    print(result is None)

    # Containers
    tags = ["python", "rag", "fastapi"]          # list: ordered, mutable
    point = (3, 4)                               # tuple: ordered, immutable
    scores = {"chunking": 8, "retrieval": 7}     # dict: key -> value
    unique = {1, 2, 2, 3}                        # set: unique items

    tags.append("pinecone")
    print(tags, point, scores, unique)

    # Type conversion
    print(int("100"), float("2.5"), str(123), list("abc"))

    # Checking types
    print(isinstance(price, float), isinstance(count, str))


if __name__ == "__main__":
    main()
