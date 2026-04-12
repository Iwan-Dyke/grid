# command_routing — Design

## Purpose

Typer CLI application. Routes user commands to the appropriate service operations. Handles interactive wizards and scripting-friendly flag interfaces.

---

## Dependencies

- `note_modeling` — value objects
- `service.py` — orchestration layer
- `typer` — CLI framework (MIT)
- `rich` — terminal output formatting (MIT)

All dependencies must be open source with a permissive license (MIT, BSD, Apache 2.0).

---

## Commands

### `grid new`

Create a new note.

- **Wizard mode** (default): prompts for title, type, tags, initial links (fuzzy search by title)
- **Flag mode**: `grid new --title "My Note" --tags rdf,linked-data`
- Generates ID (`YYYYMMDDHHMMSS` UTC), creates file, opens in `$EDITOR`
- Auto-runs sync after editor closes

### `grid link`

Add a link to an existing note.

- **Wizard mode**: select source note (fuzzy search), select target note, choose link type, optional label
- **Flag mode**: `grid link --from <id> --to <id> --type related --label "some label"`
- Inserts wiki-link at the **end of the source note's body**
- Auto-runs sync after insertion

### `grid sync`

Sync wiki-links from body to frontmatter.

- `grid sync <id>` — sync a single note
- `grid sync --all` — sync entire vault
- Full replace: body is source of truth

### `grid list`

List notes in the vault.

- `grid list` — all notes, sorted by modified date
- `grid list --tag <tag>` — filter by tag
- `grid list --type <type>` — filter by note type
- Filters compound: `grid list --tag rdf --type note` (AND logic)
- Output: table with ID, title, tags, modified date

### `grid show <id>`

Display a note's content and metadata.

- Default: `rich` formatted — metadata as header panel, body as rendered markdown
- `--raw` flag: raw file contents for scripting/piping

### `grid search <query>`

Fuzzy search notes by title and body content. Delegates to `service.search(query)` — search logic lives in `service.py`, not here.

Wizards in `grid new` and `grid link` also call `service.search(query)` for fuzzy title matching.

### `grid export`

Export the vault as RDF.

- `grid export --format turtle` (default)
- `grid export --format jsonld`
- `grid export --format ntriples`
- Writes to stdout or `--output <file>`

### `grid serve`

Launch the web visualisation server (delegates to `web_serving`).

### `grid query <sparql>`

Run a SPARQL query against the vault graph.

- Output as a formatted table
- `grid query --file <file.sparql>` — read query from file

---

## Build Order

Built fifth, after `service`. Tests use the Typer test runner (`CliRunner`) against a temporary vault.
