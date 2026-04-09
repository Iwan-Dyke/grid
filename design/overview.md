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

**Frontmatter schema** (inherited from weave2):

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
| `linksTo` | `weave:linksTo` | custom |
| `related` | `skos:related` | SKOS |
| `broader` | `skos:broader` | SKOS |
| `narrower` | `skos:narrower` | SKOS |
| `seeAlso` | `rdfs:seeAlso` | RDFS |
| custom | `weave:{type}` | custom |

### RDF Strategy

- Vocab preference: SKOS, FOAF, DCTERMS, schema.org — custom `weave:` namespace for domain-specific predicates
- RDF computed on-the-fly from markdown — no sidecar files
- Dual typing: `weave:Note` + `schema:Article`
- Tags typed as `skos:Concept` with `skos:prefLabel`
- Links unidirectional — reasoners infer symmetric relationships

### Authoring UX

- Primary: interactive wizard (`grid new`, `grid link`) with prompts
- Fallback: flagged subcommands for scripting and power use
- `grid sync` parses wiki-links from body and syncs to frontmatter

### Visualisation

- `grid serve` — launches local FastAPI server, opens browser
- Cytoscape.js for graph rendering (force-directed, interactive)
- Features: click node to see note content, navigate connections, filter by tag/relationship type, search box, SPARQL query interface

---

## Architecture

Hexagonal (ports and adapters).

**Dependency rule:** adapters depend on the domain; the domain depends on nothing outside itself.

- **Domain** — Note, Link, Graph, RDF projection concepts. No framework or library imports.
- **Ports** — interfaces the domain exposes or requires (`NoteRepository`, `GraphQuery`, `Exporter`)
- **Adapters** — concrete implementations per technology

### Package Structure

```
grid/
├── src/
│   └── grid/
│       ├── domain/
│       │   ├── note.py          # Note, Link value objects
│       │   ├── graph.py         # Graph, traversal logic
│       │   └── rdf.py           # RDF projection concepts (no rdflib)
│       ├── ports/
│       │   ├── repository.py    # NoteRepository interface
│       │   ├── query.py         # GraphQuery interface
│       │   └── exporter.py      # Exporter interface
│       └── adapters/
│           ├── markdown.py      # MarkdownFileRepository
│           ├── rdflib.py        # RDFlibGraph (rdflib import lives here)
│           ├── cli/             # Typer CLI + wizard
│           └── web/             # FastAPI + Cytoscape.js
├── tests/
├── justfile
├── Dockerfile
└── pyproject.toml
```

---

## Open Questions

- What does `domain/rdf.py` contain if not rdflib code? (in progress)
- Full set of `just` commands to define
- SPARQL query interface design (web UI)
- `grid sync` behaviour — auto on save, or manual command?

---

## Out of Scope (for now)

- Index persistence / caching
- File watching for incremental graph rebuild
- Import RDF → notes
- Multi-user / remote vault
