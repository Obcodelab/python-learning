"""Classes and objects.

Defining attributes in __init__ and adding instance methods.
"""


class Assignment:
    # A class-level attribute is shared by every instance.
    default_status = "pending"

    def __init__(self, title: str, course: str, weight: int = 10) -> None:
        # Instance attributes are set on `self`.
        self.title = title
        self.course = course
        self.weight = weight
        self.status = Assignment.default_status

    def submit(self) -> None:
        self.status = "submitted"

    def is_done(self) -> bool:
        return self.status == "submitted"

    # __repr__ controls how the object prints.
    def __repr__(self) -> str:
        return f"Assignment({self.title!r}, {self.course!r}, status={self.status!r})"


def main() -> None:
    a1 = Assignment("RAG report", "SIWES", weight=20)
    a2 = Assignment("Chunking exercise", "SIWES")

    print(a1)
    print(a2)

    a1.submit()
    print("a1 done?", a1.is_done())
    print("a2 done?", a2.is_done())

    # Every object knows its class
    print(type(a1).__name__)
    print(isinstance(a1, Assignment))

    # A list of objects
    todo = [a for a in (a1, a2) if not a.is_done()]
    print("still to do:", todo)


if __name__ == "__main__":
    main()
