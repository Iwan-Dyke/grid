from dataclasses import dataclass


@dataclass(frozen=True)
class Triple:
    subject: str
    predicate: str
    object: str

    def __post_init__(self):
        if not self.subject:
            raise ValueError("subject cannot be empty")
        if not self.predicate:
            raise ValueError("predicate cannot be empty")
        if not self.object:
            raise ValueError("object cannot be empty")
