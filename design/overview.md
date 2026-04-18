# Grid — Design Overview

## What It Is

Grid is a CLI tool for authoring and managing a personal knowledge graph stored as markdown notes. Notes are linked via typed RDF relationships. The graph can be explored visually via a local web interface.

Pipeline: `markdown files → Note structs → RDF triples (on-the-fly) → graph exploration / SPARQL queries / visualisation`

---

## Goals

- Author and manage a Zettelkasten-style note vault from the terminal
- Embed typed RDF relationships between notes
- Explore the resulting knowledge graph visually and via SPARQL
- Showcase clean Python architecture and linked data skills

---

## Locked-In Decisions

### Language & Tooling

| Concern | Choice |
|---|---|
| Language | Python |
| Package manager | `uv` |
| CLI framework | Typer |
| RDF library | rdflib |
| Visualisation | FastAPI + Cytoscape.js |
| Task runner | `just` |
| Containerisation | Docker |

### Vault Layout

- Flat `notes/` directory — no date-based nesting
- RDF owns all structure and relationships; folders are storage only

### ID Scheme

- Format: `YYYYMMDDHHMMSS` (UTC, second precision)
- Filename: `20260409221400-my-note-title.md`
- Canonical ID is the timestamp prefix only — title slug is for human browsability
- Title lives in frontmatter, not the ID
- IDs are permanent — renaming a note does not change its ID
- Links reference ID only: `[[20260409221400]]`
- Users never hand-type IDs — the wizard handles link authoring via fuzzy title search

### Note Structure

Frontmatter is the canonical store. Wiki-links in the body are an authoring shortcut synced back to frontmatter by the tool. RDF projection reads frontmatter only.

**Frontmatter schema**:

```yaml
id: "20260409221400"
title: "My Note Title"
type: "note"
created: "2026-04-09T22:14:00Z"
modified: "2026-04-09T22:14:00Z"
tags:
  - rdf
  - linked-data
links:
  - id: "20260101120000"
    type: "related"
    label: "optional label"
```

### Link Syntax

Supported wiki-link formats in body (synced to frontmatter):

- `[[ID]]` — default type `linksTo`
- `[[type::ID]]` — typed link
- `[[type::ID|label]]` — typed link with label

### Relationship Types

| Alias | RDF Predicate | Vocab |
|---|---|---|
| `linksTo` | `grid:linksTo` | custom |
| `related` | `skos:related` | SKOS |
| `broader` | `skos:broader` | SKOS |
| `narrower` | `skos:narrower` | SKOS |
| `seeAlso` | `rdfs:seeAlso` | RDFS |
| custom | `grid:{type}` | custom |

### RDF Strategy

- Vocab preference: SKOS, DCTERMS, schema.org — custom `grid:` namespace for domain-specific predicates
- Additional namespaces (e.g. FOAF) are user-configurable via config — not shipped by default
- RDF computed on-the-fly from markdown — no sidecar files
- Dual typing: `grid:Note` + `schema:Article`
- Tags typed as `skos:Concept` with `skos:prefLabel`
- Links are unidirectional by default; the rdflib adapter hardcodes symmetry for specific predicates:
  - `skos:related` — emit both directions
  - `skos:broader` / `skos:narrower` — emit the inverse automatically
  - All other predicates (`grid:linksTo`, `rdfs:seeAlso`, custom) — unidirectional only

### Authoring UX

- Primary: interactive wizard (`grid new`, `grid link`) with prompts
- Fallback: flagged subcommands for scripting and power use
- `grid link` inserts wiki-links into the note body (not directly into frontmatter)
- `grid sync` parses wiki-links from body and fully replaces the `links:` array in frontmatter
- Flow is always: body → sync → frontmatter (body is the single source of truth for links)
- `service` auto-reconciles on load: every note returned to callers has already been synced, and if sync changed the note the updated version is written back to disk. `grid sync` remains the explicit batch command but is no longer required for consumers (CLI, web, RDF projection) to observe current truth
- `vault_parsing.parse_note` stays a pure parser — it returns whatever is on disk. The orchestration (parse → sync → persist-if-changed) lives in `service`

### Visualisation

- `grid serve` — launches local FastAPI server, opens browser
- Cytoscape.js for graph rendering (force-directed, interactive)
- Phase 1: graph visualization — click node to see note content, navigate connections, filter by tag/relationship type, search box
- Phase 2: SPARQL query interface (text input → `service.query_sparql()` → results table)

---

## Architecture

Modular with clear dependency boundaries. Ports (interfaces) defined as Python `Protocol` classes in `note_modeling/`.

**Dependency rule:** outer modules depend on inner modules; `note_modeling` depends on nothing outside itself.

```
note_modeling → vault_parsing → rdf_projection → service → command_routing
                                                          → web_serving
```

### Modules

| Module | Responsibility |
|---|---|
| `note_modeling/` | Note, Link, Tag value objects, graph traversal, port definitions (Protocols) |
| `vault_parsing/` | Markdown parsing, frontmatter read/write, wiki-link extraction, sync logic |
| `rdf_projection/` | Note → RDF triples, symmetry rules, SPARQL queries, serialization |
| `service.py` | Orchestration layer — shared entry point for `command_routing` and `web_serving` |
| `command_routing/` | Typer CLI commands, wizard flows, scripting flags |
| `web_serving/` | FastAPI server, Cytoscape.js frontend, graph API endpoints |

### Package Structure

```
grid/
├── grid/
│   ├── note_modeling/      # Core domain — no external dependencies
│   ├── vault_parsing/      # Markdown ↔ Note conversion, sync
│   ├── rdf_projection/     # RDF projection, SPARQL, serialization
│   ├── command_routing/    # Typer CLI + wizards
│   ├── web_serving/        # FastAPI + Cytoscape.js
│   └── service.py          # Orchestration layer tying modules together
├── tests/
├── justfile
├── Dockerfile
└── pyproject.toml
```

---

## Just Commands

| Command | What it does |
|---|---|
| `just dev` | `uv run --with . grid` — isolated temporary env for testing (no side effects) |
| `just install` | `uv pip install -e .` — editable install for development |
| `just build` | `python -m build --check` — validate package is well-formed |
| `just test` | run pytest |
| `just lint` | run ruff check |
| `just fmt` | run ruff format |
| `just clean` | remove build artifacts |
| `just docker-build` | build Docker image |
| `just docker-run` | run via Docker |

---

## Out of Scope (for now)

- Index persistence / caching
- Import RDF → notes
- Multi-user / remote vault
