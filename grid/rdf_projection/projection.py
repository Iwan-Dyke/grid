from grid.note_modeling import IRI, Link, Note, Tag, Triple
from grid.rdf_projection.namespaces import DCTERMS, RDF, RDFS, SCHEMA, SKOS


RDF_TYPE = IRI(f"{RDF}type")


SYMMETRIC_PREDICATES = {"related"}
INVERSE_PREDICATES = {"broader": "narrower", "narrower": "broader"}
RESERVED_LINK_TYPES = {"linksTo", "related", "broader", "narrower", "seeAlso"}


def project(notes: list[Note], grid_uri: str) -> list[Triple]:
    triples: list[Triple] = []
    for note in notes:
        triples.extend(_note_triples(note, grid_uri))
        for tag in note.tags:
            triples.extend(_tag_triples(note, tag, grid_uri))
        for link in note.links:
            triples.extend(_link_triples(note, link, grid_uri))
    return triples


def _note_iri(note_id: str, grid_uri: str) -> IRI:
    return IRI(f"{grid_uri}{note_id}")


def _tag_iri(tag_name: str, grid_uri: str) -> IRI:
    return IRI(f"{grid_uri}tag-{tag_name}")


def _note_triples(note: Note, grid_uri: str) -> list[Triple]:
    subject = _note_iri(note.id, grid_uri)
    return [
        Triple(subject, RDF_TYPE, IRI(f"{grid_uri}Note")),
        Triple(subject, RDF_TYPE, IRI(f"{SCHEMA}Article")),
        Triple(subject, IRI(f"{DCTERMS}identifier"), note.id),
        Triple(subject, IRI(f"{DCTERMS}title"), note.title),
        Triple(subject, IRI(f"{DCTERMS}created"), note.created.isoformat()),
        Triple(subject, IRI(f"{DCTERMS}modified"), note.modified.isoformat()),
    ]


def _tag_triples(note: Note, tag: Tag, grid_uri: str) -> list[Triple]:
    tag_iri = _tag_iri(tag.name, grid_uri)
    return [
        Triple(tag_iri, RDF_TYPE, IRI(f"{SKOS}Concept")),
        Triple(tag_iri, IRI(f"{SKOS}prefLabel"), tag.name),
        Triple(_note_iri(note.id, grid_uri), IRI(f"{DCTERMS}subject"), tag_iri),
    ]


def _link_triples(note: Note, link: Link, grid_uri: str) -> list[Triple]:
    source = _note_iri(note.id, grid_uri)
    target = _note_iri(link.target_id, grid_uri)
    predicate = _predicate_for(link.link_type, grid_uri)
    triples = [Triple(source, predicate, target)]

    if link.link_type in SYMMETRIC_PREDICATES:
        triples.append(Triple(target, predicate, source))
    elif link.link_type in INVERSE_PREDICATES:
        inverse = _predicate_for(INVERSE_PREDICATES[link.link_type], grid_uri)
        triples.append(Triple(target, inverse, source))

    return triples


def _predicate_for(link_type: str, grid_uri: str) -> IRI:
    if link_type == "related":
        return IRI(f"{SKOS}related")
    if link_type == "broader":
        return IRI(f"{SKOS}broader")
    if link_type == "narrower":
        return IRI(f"{SKOS}narrower")
    if link_type == "seeAlso":
        return IRI(f"{RDFS}seeAlso")
    return IRI(f"{grid_uri}{link_type}")
