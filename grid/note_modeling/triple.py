from dataclasses import dataclass


class IRI(str):
    """Marker subclass for strings that denote an IRI rather than a literal.

    A `Triple.object` that is an `IRI` should be converted to a resource
    reference by downstream adapters; a plain `str` should be treated as a
    literal value. `IRI` compares equal to its underlying string so existing
    string-based equality checks continue to work.
    """

    __slots__ = ()


class TypedLiteral(str):
    """Marker subclass for literal strings that carry an xsd datatype.

    Adapters use this to mint rdflib `Literal` with the correct datatype
    rather than keying off the predicate IRI. The producer declares intent
    at projection time; downstream code does not have to know which
    predicates take which datatypes.
    """

    __slots__ = ("datatype",)

    def __new__(cls, value: str, datatype: str) -> "TypedLiteral":
        instance = super().__new__(cls, value)
        instance.datatype = datatype
        return instance


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
