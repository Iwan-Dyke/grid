# vault_parsing — Design

## Purpose

Read and write markdown note files. Parse frontmatter, extract wiki-links from body, and run the sync operation (body → frontmatter). Implements `NoteRepository`.

---

## Dependencies

- `note_modeling` — consumes Note, Link, Tag value objects and implements `NoteRepository` protocol
- `python-frontmatter` — YAML frontmatter parsing and serialization
- `python-slugify` — filename slug generation with non-ASCII transliteration
- `re` (stdlib) — wiki-link regex extraction

---

## Responsibilities

- Parse a markdown file into a `Note` value object
- Serialize a `Note` back to markdown (frontmatter + body)
- Extract wiki-links from body text using regex
- Sync: parse body wiki-links → rebuild `links:` array in frontmatter
- Generate note filenames from ID + title slug (transliterate non-ASCII)
- Implement `NoteRepository` protocol against a flat `notes/` directory

---

## Wiki-Link Parsing

Single combined regex, one pass, no ordering ambiguity:

```python
\[\[(?:(\w+)::)?(\d{14})(?:\|(.+?))?\]\]
```

Three supported formats only:

| Format | Example | Result |
|---|---|---|
| `[[ID]]` | `[[20260409221400]]` | type=`linksTo`, no label |
| `[[type::ID]]` | `[[related::20260409221400]]` | typed, no label |
| `[[type::ID\|label]]` | `[[related::20260409221400\|see this]]` | typed with label |

`[[ID|label]]` (label without type) is **not supported** — if you want a label, specify the type.

---

## Sync Logic

`sync(note: Note) -> Note`:

1. Parse all wiki-links from `note.body`
2. Build new `links` tuple from extracted wiki-links
3. Compare old links to new links — if unchanged, return original `Note` (no `modified` bump)
4. If changed, return new `Note` with updated `links` and `modified` timestamp
5. Caller is responsible for saving via `NoteRepository.save`

Sync is a **full replace** — any links in frontmatter not present in the body are removed.

---

## File Operations

### Filename Convention

`{id}-{slugified-title}.md` — e.g. `20260409221400-my-note-title.md`

Slug generation uses `python-slugify` for non-ASCII transliteration (e.g. "Über" → "uber").

### MarkdownFileRepository

```python
class MarkdownFileRepository:
    def __init__(self, vault_path: Path): ...
    def load(self, note_id: str) -> Note: ...
    def load_all(self) -> list[Note]: ...
    def load_raw(self, note_id: str) -> str: ...
    def save(self, note: Note) -> None: ...
    def delete(self, note_id: str) -> None: ...
    def exists(self, note_id: str) -> bool: ...
```

- `load_all` globs `*.md`, parses each, builds an in-memory `dict[str, Path]` index (ID → filepath)
- `load` uses the index for direct lookup after first `load_all`; O(1) instead of O(n) directory scan
- `save` writes frontmatter + body

---

## Error Handling

Exception-based, following Kelvin Henney's approach — exceptions for exceptional circumstances, not flow control.

| Scenario | Handling |
|---|---|
| Malformed frontmatter | Raise `NoteParseError` |
| File not found on `load` | Raise `NoteNotFoundError` |
| Duplicate IDs | Raise |
| Dangling links (target ID doesn't exist) | Store as-is — valid state, target may not exist yet |

---

## Build Order

Built second, after `note_modeling`. Tests use real temporary directories (no mocks for file I/O — test the actual parsing).
