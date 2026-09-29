"""Python syntax and basics: no semicolons or braces (indentation defines
blocks), no required type declarations, no keyword needed to declare a
variable."""


def main() -> None:
    # Printing and string formatting
    name = "SIWES"
    week = 19
    print("Program:", name, "week", week)
    print(f"Program: {name}, week {week}")  # f-string

    # Indentation instead of braces
    if week >= 19:
        print("Python phase has started")

    # Multiple assignment
    a, b = 1, 2
    a, b = b, a
    print("after swap:", a, b)

    # Truthiness: empty containers, 0 and None are falsy
    for value in [0, "", [], None, "text", 5]:
        print(repr(value), "->", bool(value))

    # Comments start with '#'. This string below is a docstring-style note,
    # not a real comment, but Python ignores an expression statement like this.
    "dynamic typing means the same name can point at different types"
    x = 10
    print(type(x))
    x = "now a string"
    print(type(x))


if __name__ == "__main__":
    main()
