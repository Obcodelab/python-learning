"""Inheritance: a child class extends a parent and can override its methods.
super() calls back into the parent."""

from abc import ABC, abstractmethod


class Document(ABC):
    """Base class shared by every document type."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def extract_text(self) -> str:
        """Each document type must say how it produces text."""

    def summary(self) -> str:
        text = self.extract_text()
        return f"{self.name}: {len(text)} characters"


class TextDocument(Document):
    def __init__(self, name: str, body: str) -> None:
        super().__init__(name)          # run the parent's __init__ first
        self.body = body

    def extract_text(self) -> str:
        return self.body


class MarkdownDocument(TextDocument):
    def extract_text(self) -> str:
        # Override: strip a few Markdown markers, then reuse the parent version.
        raw = super().extract_text()
        return raw.replace("#", "").replace("*", "").strip()


def main() -> None:
    docs = [
        TextDocument("notes.txt", "plain notes about embeddings"),
        MarkdownDocument("readme.md", "# Title\n\n**bold** text here"),
    ]

    for doc in docs:
        print(doc.summary())
        print("  text:", repr(doc.extract_text()))

    # Both subclasses are still Documents
    print(all(isinstance(d, Document) for d in docs))


if __name__ == "__main__":
    main()
