from rdflib import Graph as RDFGraph, Literal, Namespace, URIRef

from grid.note_modeling import IRI, Note, Triple
from grid.rdf_projection.namespaces import (
    BUILTIN_PREFIXES,
    DEFAULT_GRID_URI,
    XSD,
)
from grid.rdf_projection.projection import project

DATETIME_PREDICATES = {
    "http://purl.org/dc/terms/created",
    "http://purl.org/dc/terms/modified",
}


class RDFlibGraphQuery:
    def __init__(
        self,
        grid_uri: str = DEFAULT_GRID_URI,
        extra_namespaces: dict[str, str] | None = None,
    ):
        self._grid_uri = grid_uri
        self._extra_namespaces = dict(extra_namespaces or {})
        self._graph: RDFGraph | None = None

    @property
    def prefixes(self) -> dict[str, str]:
        return {"grid": self._grid_uri, **BUILTIN_PREFIXES, **self._extra_namespaces}

    def build(self, notes: list[Note]) -> list[Triple]:
        triples = project(notes, self._grid_uri)
        self._graph = self._to_graph(triples)
        return triples

    def query(self, sparql: str) -> list[dict]:
        if self._graph is None:
            self._graph = RDFGraph()
        prelude = "\n".join(
            f"PREFIX {prefix}: <{uri}>" for prefix, uri in self.prefixes.items()
        )
        full_query = f"{prelude}\n{sparql}"
        results = self._graph.query(full_query)
        return [
            {str(var): _serialize_term(row[var]) for var in results.vars}
            for row in results
        ]

    def serialize(self, format: str = "turtle") -> str:
        if self._graph is None:
            self._graph = RDFGraph()
        return self._graph.serialize(format=format)

    def _to_graph(self, triples: list[Triple]) -> RDFGraph:
        g = RDFGraph()
        for prefix, uri in self.prefixes.items():
            g.bind(prefix, Namespace(uri))
        for triple in triples:
            g.add(self._convert(triple))
        return g

    def _convert(self, triple: Triple):
        subject = URIRef(triple.subject)
        predicate = URIRef(triple.predicate)
        if isinstance(triple.object, IRI):
            return (subject, predicate, URIRef(triple.object))
        if triple.predicate in DATETIME_PREDICATES:
            return (subject, predicate, Literal(triple.object, datatype=XSD.dateTime))
        return (subject, predicate, Literal(triple.object))


def _serialize_term(term):
    if term is None:
        return None
    if isinstance(term, URIRef):
        return str(term)
    if isinstance(term, Literal):
        return term.toPython()
    return str(term)
