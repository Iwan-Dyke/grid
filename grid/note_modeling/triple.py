from dataclasses import dataclass


class IRI(str):
    """Marker subclass for strings that denote an IRI rather than a literal.

    A `Triple.object` that is an `IRI` should be converted to a resource
    reference by downstream adapters; a plain `str` should be treated as a
    literal value. `IRI` compares equal to its underlying string so existing
    string-based equality checks continue to work.
    """

    __slots__ = ()


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
