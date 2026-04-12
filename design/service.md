# service — Design

## Purpose

Orchestration layer. Coordinates `note_modeling`, `vault_parsing`, and `rdf_projection` into coherent operations. Both `command_routing` and `web_serving` depend on this module — it is the single shared entry point for all orchestration.

---

## Dependencies

- `note_modeling` — Note, Graph, NoteRepository value objects and protocols
- `rdf_projection` — `RDFlibGraphQuery`
- `thefuzz` — fuzzy string matching for search (MIT)

All dependencies must be open source with a permissive license (MIT, BSD, Apache 2.0).

---

## Responsibilities

- Load the vault into an in-memory `Graph`
- Expose search across notes (fuzzy title + body)
- Orchestrate note creation, linking, and sync
- Delegate SPARQL queries and RDF export to `rdf_projection`

---

## Interface

### Vault Loading

```python
def load_graph(repo: NoteRepository) -> Graph: ...
```

Loads all notes via `repo.load_all()`, builds and returns an in-memory `Graph`. Caller is responsible for creating the `MarkdownFileRepository` and passing it in.

### Search

```python
def search(graph: Graph, query: str) -> list[Note]: ...
```

Fuzzy match against note titles and body content using `thefuzz`. Used by `command_routing` wizards and `grid search`, and by `web_serving` `/api/search`.

### Raw File Access

```python
def get_raw(repo: NoteRepository, note_id: str) -> str: ...
```

Returns raw file contents for a note. Used by `grid show --raw`. Delegates to `repo.load_raw()`.

### Note Operations

```python
def create_note(repo: NoteRepository, title: str, note_type: str, tags: list[str]) -> Note: ...
def add_link(repo: NoteRepository, source_id: str, target_id: str, link_type: str, label: str | None = None) -> Note: ...
def sync_note(repo: NoteRepository, note_id: str) -> Note: ...
def sync_all(repo: NoteRepository) -> list[Note]: ...
def list_notes(graph: Graph, tag: str | None = None, note_type: str | None = None) -> list[Note]: ...
```

- `create_note` — generates ID, builds `Note`, saves via repo
- `add_link` — loads source note, appends wiki-link to body, runs sync, saves result
- `sync_note` / `sync_all` — delegate to `vault_parsing` sync logic, save result
- `list_notes` — composes `Graph` primitives for compound filtering, returns results sorted by modified date descending; `Graph` is a container not a query engine so type filtering lives here

### RDF

```python
def export_rdf(graph: Graph, format: str = "turtle") -> str: ...
def query_sparql(graph: Graph, sparql: str) -> list[dict]: ...
```

- `export_rdf` — builds triples via `RDFlibGraphQuery`, serializes to requested format
- `query_sparql` — builds triples, executes SPARQL, returns result rows

---

## Build Order

Built after `rdf_projection`, before `command_routing` and `web_serving`. Tests use a temporary vault with real files — no mocks.
