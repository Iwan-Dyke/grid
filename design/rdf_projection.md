# rdf_projection — Design

## Purpose

Project `Note` value objects into RDF triples using rdflib. Handle symmetry rules, SPARQL query execution, and serialization to standard formats. Implements `GraphQuery`.

---

## Dependencies

- `note_modeling` — consumes Note, Link, Tag, Triple value objects and implements `GraphQuery` protocol
- `rdflib` — triple store, SPARQL, serialization

---

## Responsibilities

- Convert a list of `Note` objects into domain `Triple` objects (projection logic)
- Convert `Triple` objects into an rdflib `Graph` (one-way, no round-trip)
- Apply symmetry rules for specific predicates
- Execute SPARQL queries against the in-memory graph
- Serialize the graph to Turtle, N-Triples, or JSON-LD

---

## Data Flow

```
list[Note] → build() → list[Triple] → to_graph() → rdflib.Graph → query() / serialize()
```

- `build` is the protocol method — produces domain `Triple` objects, easy to test
- `to_graph` is internal — converts `Triple` to rdflib objects, no round-trip conversion needed
- Projection wraps IRI-valued strings in `IRI(...)` (see `note_modeling`); the adapter then uses `isinstance(triple.object, IRI)` to decide IRI-vs-literal. No heuristic sniffing at the adapter boundary — the producer declares intent.

---

## Namespace Bindings

Built-in defaults:

```python
GRID    = Namespace("https://grid.example/ns/")  # default; overridable
SKOS    = Namespace("http://www.w3.org/2004/02/skos/core#")
SCHEMA  = Namespace("https://schema.org/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
RDFS    = Namespace("http://www.w3.org/2000/01/rdf-schema#")
XSD     = Namespace("http://www.w3.org/2001/XMLSchema#")
```

The `grid:` default uses the RFC 2606 reserved `example` TLD so the IRI never collides with a real domain. Users can override both the `grid:` namespace and add arbitrary prefixes via the `RDFlibGraphQuery` constructor:

```python
RDFlibGraphQuery(
    grid_uri="https://my-real-domain.com/grid/",
    extra_namespaces={"foaf": "http://xmlns.com/foaf/0.1/"},
)
```

When the project grows a config layer, the same constructor args are wired from YAML — no projection-layer changes needed.

---

## Projection Rules

### Note → Triples

For each `Note`:

```turtle
grid:{id} a grid:Note, schema:Article ;
    dcterms:identifier "{id}" ;
    dcterms:title "{title}" ;
    dcterms:created "{created}"^^xsd:dateTime ;
    dcterms:modified "{modified}"^^xsd:dateTime .
```

### Tag → Triples

For each tag on a note:

```turtle
grid:tag-{name} a skos:Concept ;
    skos:prefLabel "{name}" .

grid:{note_id} dcterms:subject grid:tag-{name} .
```

### Link → Triples

| Link Type | Triple |
|---|---|
| `linksTo` | `grid:{source} grid:linksTo grid:{target}` |
| `related` | `grid:{source} skos:related grid:{target}` + `grid:{target} skos:related grid:{source}` |
| `broader` | `grid:{source} skos:broader grid:{target}` + `grid:{target} skos:narrower grid:{source}` |
| `narrower` | `grid:{source} skos:narrower grid:{target}` + `grid:{target} skos:broader grid:{source}` |
| `seeAlso` | `grid:{source} rdfs:seeAlso grid:{target}` |
| custom | `grid:{source} grid:{type} grid:{target}` |

Link labels (`Link.label`) are **not projected to RDF** — they are a domain/UI concern only, displayed on edges in the web visualization.

---

## Symmetry Rules

Hardcoded in the projection logic, not via a reasoner:

- `skos:related` — emit both directions
- `skos:broader` / `skos:narrower` — emit the inverse

All other predicates are unidirectional.

---

## RDFlibGraphQuery

```python
class RDFlibGraphQuery:
    def __init__(
        self,
        grid_uri: str = DEFAULT_GRID_URI,
        extra_namespaces: dict[str, str] | None = None,
    ): ...
    def build(self, notes: list[Note]) -> list[Triple]: ...
    def query(self, sparql: str) -> list[dict]: ...
    def serialize(self, format: str = "turtle") -> str: ...
```

- `build` — protocol method, produces domain `Triple` objects and populates the internal rdflib graph
- `query` — protocol method, executes SPARQL against the internal rdflib graph
- `to_graph` — internal, converts `Triple` list to rdflib `Graph`
- `serialize` — implementation detail of `RDFlibGraphQuery` only, not part of the `GraphQuery` protocol; rdflib-specific, outputs Turtle/N-Triples/JSON-LD

### SPARQL Prefix Handling

Hybrid. `query()` auto-injects `PREFIX` declarations for every entry in `self.prefixes` (builtins + `extra_namespaces`) as a prelude to the user's SPARQL. Users writing `SELECT ?s WHERE { ?s a grid:Note }` never have to retype boilerplate. If the user's query contains their own `PREFIX` line for the same prefix, rdflib honours the user's declaration (duplicate prefixes are allowed).

---

## Build Order

Built third, after `vault_parsing`. Tests create `Note` objects directly and assert on the resulting `Triple` list.
