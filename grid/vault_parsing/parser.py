from datetime import datetime, UTC
from pathlib import Path

import frontmatter

from grid.note_modeling import Note, Tag, Link
from grid.vault_parsing.errors import NoteParseError


def parse_note(path: Path) -> Note:
    try:
        post = frontmatter.load(str(path))
    except Exception as e:
        raise NoteParseError(f"Failed to parse {path.name}: {e}") from e

    meta = post.metadata
    if "id" not in meta or "title" not in meta:
        raise NoteParseError(f"Missing required fields in {path.name}")

    tags = tuple(Tag(name=t) for t in meta.get("tags", []))
    links = tuple(deserialize_link(d) for d in meta.get("links", []))
    created = parse_datetime(meta.get("created"))
    modified = parse_datetime(meta.get("modified"))

    return Note(
        id=str(meta["id"]),
        title=meta["title"],
        note_type=meta.get("type", "note"),
        created=created,
        modified=modified,
        tags=tags,
        links=links,
        body=post.content,
    )


def serialize_note(note: Note) -> str:
    metadata = {
        "id": note.id,
        "title": note.title,
        "type": note.note_type,
        "created": note.created.isoformat(),
        "modified": note.modified.isoformat(),
        "tags": [t.name for t in note.tags],
        "links": [serialize_link(link) for link in note.links],
    }
    post = frontmatter.Post(note.body, **metadata)
    return frontmatter.dumps(post)


def serialize_link(link: Link) -> dict:
    result = {"id": link.target_id, "type": link.link_type}
    if link.label is not None:
        result["label"] = link.label
    return result


def deserialize_link(data: dict) -> Link:
    return Link(
        target_id=str(data["id"]),
        link_type=data["type"],
        label=data.get("label"),
    )


def parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    parsed = datetime.fromisoformat(str(value))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
