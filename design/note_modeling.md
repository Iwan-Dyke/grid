# note_modeling — Design

## Purpose

Define the core value objects and graph traversal logic. This module has zero external dependencies — it is pure Python. All other modules depend on it; it depends on nothing.

---

## Responsibilities

- `Note`, `Link`, `Tag`, `Triple` value objects (immutable dataclasses)
- `Graph` — in-memory mutable container for notes with traversal/query methods
- `generate_note_id()` — ID generation (domain invariant)
- Port definitions (`Protocol` classes) for repository and query interfaces

---

## Value Objects

### Note

Frozen. Edits produce a new `Note` object; the old one is discarded.

```python
@dataclass(frozen=True)
class Note:
    id: str                     # "20260409221400"
    title: str
    note_type: str              # "note" default
    created: datetime
    modified: datetime
    tags: tuple[Tag, ...]
    links: tuple[Link, ...]
    body: str
```

### Link

```python
@dataclass(frozen=True)
class Link:
    target_id: str
    link_type: str              # "linksTo", "related", "broader", etc.
    label: str | None = None
```

### Tag

Dataclass to allow validation in `__post_init__` (e.g. lowercase, no spaces, max length).

```python
@dataclass(frozen=True)
class Tag:
    name: str
```

### Triple

Domain-level RDF triple representation. Keeps the `GraphQuery` protocol independent of rdflib.

```python
@dataclass(frozen=True)
class Triple:
    subject: str
    predicate: str
    object: str
```

---

## ID Generation

ID format is a domain invariant. Lives here, not in the service layer.

```python
def generate_note_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%d%H%M%S")
```

---

## Graph

Mutable in-memory container for frozen `Note` objects. Notes are values; the graph is a collection.

```python
class Graph:
    def add(self, note: Note) -> None: ...
    def get(self, note_id: str) -> Note | None: ...
    def all_notes(self) -> list[Note]: ...
    def outgoing(self, note_id: str) -> list[Note]: ...
    def incoming(self, note_id: str) -> list[Note]: ...
    def neighbors(self, note_id: str) -> list[Note]: ...
    def filter_by_tag(self, tag: str) -> list[Note]: ...
```

- `outgoing(id)` — notes this note links to
- `incoming(id)` — notes that link to this note
- `neighbors(id)` — union of both
- Search is a CLI concern — fuzzy title/body search lives in `service.py`
- `filter_by_tag` is a structural domain primitive — tags are part of the domain model
- Compound filtering (e.g. by type + tag) and `filter_by_type` live in `service.py` — `Graph` is a container, not a query engine

---

## Ports (Protocols)

### NoteRepository

```python
class NoteRepository(Protocol):
    def load(self, note_id: str) -> Note: ...
    def load_all(self) -> list[Note]: ...
    def load_raw(self, note_id: str) -> str: ...
    def save(self, note: Note) -> None: ...
    def delete(self, note_id: str) -> None: ...
    def exists(self, note_id: str) -> bool: ...
```

### GraphQuery

```python
class GraphQuery(Protocol):
    def build(self, notes: list[Note]) -> list[Triple]: ...
    def query(self, sparql: str) -> list[dict]: ...
```

- `build` returns domain-level `Triple` objects, not rdflib types
- `to_graph` (rdflib conversion) is an internal detail of `rdf_projection`, not part of this contract

---

## Build Order

This module is built first. All tests use plain unit tests — no mocks needed since there are no dependencies.
