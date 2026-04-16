from datetime import UTC, datetime

from grid.note_modeling import Note
from grid.vault_parsing.wiki_links import extract_wiki_links


def sync(note: Note) -> Note:
    new_links = tuple(extract_wiki_links(note.body))
    if new_links == note.links:
        return note
    return Note(
        id=note.id,
        title=note.title,
        note_type=note.note_type,
        created=note.created,
        modified=datetime.now(UTC),
        tags=note.tags,
        links=new_links,
        body=note.body,
    )
