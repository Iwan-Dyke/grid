# command_routing — Design

## Purpose

Typer CLI application. Routes user commands to the appropriate service operations. Handles interactive wizards and scripting-friendly flag interfaces.

---

## Dependencies

- `note_modeling` — value objects
- `service.py` — orchestration layer
- `typer` — CLI framework (MIT)
- `rich` — terminal output formatting (MIT)
- `platformdirs` — cross-platform user data/config directory resolution (MIT)
- `tomli-w` — TOML writing (MIT). `tomllib` is used for reading (Python 3.11+ stdlib).

All dependencies must be open source with a permissive license (MIT, BSD, Apache 2.0).

---

## Config

Grid stores per-user config at the platform config directory, resolved via `platformdirs.user_config_path("grid")`:

- Linux: `~/.config/grid/config.toml`
- macOS: `~/Library/Preferences/grid/config.toml`
- Windows: `%APPDATA%\grid\config.toml`

### Schema

```toml
default = "work"

[vaults.work]
path = "/home/dykei/notes/work"

[vaults.personal]
path = "/home/dykei/notes/personal"
```

- `default` — name of the default vault. Must reference a key under `[vaults]`.
- `[vaults.<name>]` — one section per registered vault. `<name>` is a unique alias, constrained to `^[a-zA-Z0-9_-]+$` (letters, digits, hyphen, underscore — matches TOML bare-key grammar and guarantees unambiguous name-vs-path distinction: any `--vault <value>` containing `/` or `\` or a `.` is treated as a path, skipping name lookup).
- `path` — absolute filesystem path to the vault directory.

The config file is created on the first successful `grid init` and updated whenever a vault is added or the default changes. Missing config is not an error — commands fall back to the platform default data directory (see "Vault Resolution").

Grid does not delete or edit on-disk vault contents when the config changes — config is purely about registration and default selection.

---

## Vault Resolution

Every command locates the vault through a shared resolution order (highest priority first):

1. `--vault <name-or-path>` flag. The value is classified as a path (and resolved to an absolute filesystem path) if it contains any of `/`, `\`, or `.` — otherwise it is classified as a bare name and looked up in `[vaults]`. Bare names that don't match a registered vault raise `UnknownVaultError` (exit 1) with guidance to use `./<name>` for a relative path — silent creation of a new vault from a typo'd name would hide the error and is therefore rejected.
2. `GRID_VAULT` environment variable — treated as a filesystem path only (no name lookup).
3. Config default vault — the `default` entry's path in `[vaults.<default>]`.
4. Platform default data directory via `platformdirs.user_data_path("grid") / "vault"`:
   - Linux: `~/.local/share/grid/vault/`
   - macOS: `~/Library/Application Support/grid/vault/`
   - Windows: `%LOCALAPPDATA%\grid\vault\`

The platform default is hidden by design — notes are app-managed data, not user documents to browse. It serves as a fallback for fresh installs with no config yet. Once any vault is initialised and registered in config, the config's default takes over.

Commands other than `grid init` require the resolved path to exist; if it doesn't, they error with guidance to run `grid init`.

---

## Commands

### `grid init`

Create a vault on disk and register it in the config. Supports flag mode (scripting) and wizard mode (interactive).

**Flags**: `--vault <path>`, `--name <name>`, `--default`, `--force`.

**Mode activation**:

- **Wizard mode** runs when all of: `--vault` is absent, `GRID_VAULT` is unset, and stdin is a TTY. The user is prompted for path, name, and default status.
- **Flag mode** runs otherwise. In non-TTY contexts with no `--vault`, the command errors: a script must be explicit.

**Path resolution**: follows the rules in "Vault Resolution". Relative paths are resolved to absolute before any action; the output always prints the absolute path.

**Directory state detection** — the resolved path falls into one of four states (applies to both modes):

| State | Criterion | Behaviour |
|---|---|---|
| Absent | path does not exist | Create the directory (and any missing parents). Stdout: "Initialised vault at `<path>`". Exit 0. |
| Empty-or-existing-vault | directory exists; its non-hidden entries are either zero or all match `\d{14}-*.md` | Idempotent. Stdout: "Vault already exists at `<path>`". Exit 0. |
| Has non-grid content | directory exists; at least one non-hidden entry is not a grid-style note | Without `--force` (flag mode) or a "no" answer to the wizard's adopt prompt: stderr error "Directory at `<path>` is not empty and does not look like a vault. Pass --force to adopt it anyway." Exit 1. With `--force` or "yes": stdout "Initialised vault at `<path>` (forced over existing contents)". Exit 0. Existing files are never modified or deleted. |
| Not a directory | path exists but is a file, symlink to a file, socket, etc. | Stderr error. Exit 1. `--force` does **not** override this — a file is not convertible to a directory. |

**Hidden entries** (names starting with `.`, e.g. `.git/`, `.gitignore`, `.DS_Store`) are excluded from the emptiness and grid-shape checks. This keeps version-controlled vaults and OS metadata from triggering the non-grid-content branch.

**Config registration** (runs after successful directory creation/adoption):

1. If the resolved path is already registered under some name → no-op on the config side; append "already registered as '`<name>`'" to the stdout message. A `--name` flag (or wizard name answer) that differs from the existing name is silently ignored — the existing name wins. Renaming is a separate, explicit operation (see `grid vault rename` below).
2. If the path is new and the chosen name is unused → add `[vaults.<name>] path = <abs_path>` to the config.
3. If the name collides with an existing entry at a different path → error "Vault named '`<name>`' already exists at a different path." In wizard mode, re-prompt for a name. In flag mode, exit 1.

**Name handling**:

- Flag mode: `--name <name>` explicit; if omitted, defaults to `basename(path)`.
- Wizard mode: prompts `Name for this vault? [<basename>]` with basename as default.

**Default handling**:

- **First vault ever** (no config file, or config has an empty `[vaults]` table): the vault is silently set as default regardless of mode. No prompt, no `--default` flag needed.
- **Subsequent vaults**:
  - Flag mode: `--default` makes it the new default; without it, the vault is registered but the existing default is preserved.
  - Wizard mode: prompt `Make this the new default vault? [y/N]` — default N to preserve existing.

**Wizard flow** (only when activated):

1. `Where should the vault live?` — numbered choice: `[1] Default location (<platform_default>)` and `[2] Custom path`. Default `1`.
2. If `2`: `Vault path:` — free-form string.
3. `Name for this vault? [<basename>]` — default to basename of path.
4. (Only if a default already exists) `Make this the new default vault? [y/N]`.
5. (Only if the resolved path has non-grid content) `Directory is not empty and does not look like a vault. Adopt anyway? [y/N]` — the TTY-equivalent of `--force`.
6. On success: print the standard directory-detection message plus `Registered vault '<name>' at <path>.` If the vault was not set as default, also print a hint on how to target it: `Use 'grid --vault <name>' to work with this vault.`

**Exit codes**: 0 on success, 1 on any error. Success messages go to stdout; errors to stderr.

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

## Planned — Vault Management

These commands are not yet implemented. They are documented here so the naming and scope decisions from earlier discussions aren't lost.

### `grid vault rename <old-name> <new-name>`

Rename a registered vault alias in the config. The on-disk path is unchanged; only the `[vaults.<name>]` key in config is updated, and if the renamed vault was the default, the `default` entry is updated to match.

- Errors if `<old-name>` does not exist in config.
- Errors if `<new-name>` is already used by a different vault.
- `grid init` deliberately does not rename — it always preserves existing names on already-registered paths. This command is the only supported way to change a vault's alias.

Additional vault-management commands (e.g. `grid vault list`, `grid vault remove`, `grid vault set-default`) may follow as needs arise; they share the same config-only, non-destructive stance.

---

## Build Order

Built fifth, after `service`. Tests use the Typer test runner (`CliRunner`) against a temporary vault.
