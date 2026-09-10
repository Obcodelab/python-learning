"""Functions: default, keyword, and variable-length arguments.

Also shows returning multiple values with a tuple.
"""


def greet(name: str, greeting: str = "Hello") -> str:
    """greeting has a default value, so it is optional."""
    return f"{greeting}, {name}"


def make_user(**fields) -> dict:
    """**kwargs collects keyword arguments into a dict."""
    fields.setdefault("role", "student")
    return fields


def total(*numbers) -> int:
    """*args collects positional arguments into a tuple."""
    running = 0
    for number in numbers:
        running += number
    return running


def split_name(full_name: str) -> tuple[str, str]:
    """Returns two values; Python packs them into a tuple."""
    first, _, last = full_name.partition(" ")
    return first, last


def main() -> None:
    print(greet("Ada"))
    print(greet("Ada", greeting="Welcome"))       # keyword argument
    print(greet(greeting="Hi", name="Grace"))     # order does not matter for keywords

    print(make_user(name="Ada", email="ada@example.com"))
    print(total(1, 2, 3, 4, 5))

    first, last = split_name("Grace Hopper")      # tuple unpacking
    print(first, last)

    # A function is just a value; it can be passed around
    def apply(func, value):
        return func(value)

    print(apply(str.upper, "rag"))

    # Lambda: a short anonymous function
    doubled = list(map(lambda x: x * 2, [1, 2, 3]))
    print(doubled)


if __name__ == "__main__":
    main()
