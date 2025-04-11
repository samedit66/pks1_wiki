from dataclasses import dataclass


@dataclass
class Article:
    title: str
    content: str
    image: str | None = None
    id: int | None = None
