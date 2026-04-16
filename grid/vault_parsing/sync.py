from dataclasses import dataclass
from datetime import UTC, datetime

from grid.note_modeling import Note
from grid.vault_parsing.wiki_links import AmbiguousLink, extract_wiki_links


@dataclass(frozen=True)
class SyncResult:
    note: Note
    changed: bool
    ambiguous: list[AmbiguousLink]


def sync(note: Note, now: datetime | None = None) -> SyncResult:
    parse_result = extract_wiki_links(note.body)
    new_links = tuple(parse_result.links)
    changed = new_links != note.links
    if not changed:
        return SyncResult(note=note, changed=False, ambiguous=parse_result.ambiguous)
    updated = Note(
        id=note.id,
        title=note.title,
        note_type=note.note_type,
        created=note.created,
        modified=now or datetime.now(UTC),
        tags=note.tags,
        links=new_links,
        body=note.body,
    )
    return SyncResult(note=updated, changed=True, ambiguous=parse_result.ambiguous)
