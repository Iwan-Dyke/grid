from datetime import UTC, datetime

from thefuzz import fuzz

from grid.note_modeling import (
    Graph,
    Note,
    NoteRepository,
    Tag,
    generate_note_id,
)
from grid.rdf_projection import RDFlibGraphQuery
from grid.vault_parsing import sync

SEARCH_THRESHOLD = 60


def load_graph(repo: NoteRepository) -> Graph:
    graph = Graph()
    for note in repo.load_all():
        graph.add(_reconcile(repo, note))
    return graph


def load_note(repo: NoteRepository, note_id: str) -> Note:
    return _reconcile(repo, repo.load(note_id))


def get_raw(repo: NoteRepository, note_id: str) -> str:
    return repo.load_raw(note_id)


def create_note(
    repo: NoteRepository,
    title: str,
    note_type: str,
    tags: list[str],
) -> Note:
    now = datetime.now(UTC)
    note = Note(
        id=generate_note_id(),
        title=title,
        note_type=note_type,
        created=now,
        modified=now,
        tags=tuple(Tag(name=t) for t in tags),
        links=(),
        body="",
    )
    repo.save(note)
    return note


def add_link(
    repo: NoteRepository,
    source_id: str,
    target_id: str,
    link_type: str,
    label: str | None = None,
) -> Note:
    source = repo.load(source_id)
    wiki_link = _format_wiki_link(target_id, link_type, label)
    separator = "" if not source.body or source.body.endswith("\n") else "\n"
    new_body = f"{source.body}{separator}{wiki_link}\n"
    staged = Note(
        id=source.id,
        title=source.title,
        note_type=source.note_type,
        created=source.created,
        modified=source.modified,
        tags=source.tags,
        links=source.links,
        body=new_body,
    )
    reconciled = sync(staged).note
    repo.save(reconciled)
    return reconciled


def sync_note(repo: NoteRepository, note_id: str) -> Note:
    return load_note(repo, note_id)


def sync_all(repo: NoteRepository) -> list[Note]:
    return [_reconcile(repo, note) for note in repo.load_all()]


def list_notes(
    graph: Graph,
    tag: str | None = None,
    note_type: str | None = None,
) -> list[Note]:
    notes = graph.filter_by_tag(tag) if tag is not None else graph.all_notes()
    if note_type is not None:
        notes = [n for n in notes if n.note_type == note_type]
    return sorted(notes, key=lambda n: n.modified, reverse=True)


def search(graph: Graph, query: str) -> list[Note]:
    needle = query.strip().lower()
    if not needle:
        return []
    scored: list[tuple[int, Note]] = []
    for note in graph.all_notes():
        score = max(
            fuzz.partial_ratio(needle, note.title.lower()),
            fuzz.partial_ratio(needle, note.body.lower()),
        )
        if score >= SEARCH_THRESHOLD:
            scored.append((score, note))
    scored.sort(key=lambda pair: (-pair[0], pair[1].modified))
    return [note for _, note in scored]


def export_rdf(graph: Graph, format: str = "turtle") -> str:
    projector = RDFlibGraphQuery()
    projector.build(graph.all_notes())
    return projector.serialize(format=format)


def query_sparql(graph: Graph, sparql: str) -> list[dict]:
    projector = RDFlibGraphQuery()
    projector.build(graph.all_notes())
    return projector.query(sparql)


def _reconcile(repo: NoteRepository, note: Note) -> Note:
    result = sync(note)
    if result.changed:
        repo.save(result.note)
    return result.note


def _format_wiki_link(target_id: str, link_type: str, label: str | None) -> str:
    if label is not None:
        return f"[[{link_type}::{target_id}|{label}]]"
    if link_type == "linksTo":
        return f"[[{target_id}]]"
    return f"[[{link_type}::{target_id}]]"
