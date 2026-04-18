import re
from dataclasses import dataclass

from grid.note_modeling import Link

WIKI_LINK_PATTERN = re.compile(r"\[\[([^\[\]]+?)\]\]")
STRICT_CONTENT_PATTERN = re.compile(r"^(?:(\w+)::)?(\d{14})(?:\|(.+))?$")
ID_PATTERN = re.compile(r"\d{14}")


@dataclass(frozen=True)
class AmbiguousLink:
    target_id: str
    label: str
    raw: str


@dataclass(frozen=True)
class MalformedLink:
    raw: str


@dataclass(frozen=True)
class ParseResult:
    links: tuple[Link, ...]
    ambiguous: tuple[AmbiguousLink, ...]
    malformed: tuple[MalformedLink, ...]


def extract_wiki_links(body: str) -> ParseResult:
    seen = set()
    links = []
    ambiguous = []
    malformed = []
    for match in WIKI_LINK_PATTERN.finditer(body):
        content = match.group(1)
        strict = STRICT_CONTENT_PATTERN.fullmatch(content)

        if not strict:
            if "::" in content and ID_PATTERN.search(content):
                malformed.append(MalformedLink(raw=match.group(0)))
            continue

        link_type = strict.group(1)
        target_id = strict.group(2)
        label = strict.group(3)

        if label and not link_type:
            ambiguous.append(AmbiguousLink(
                target_id=target_id,
                label=label,
                raw=match.group(0),
            ))
            key = (target_id, "linksTo", None)
            if key not in seen:
                seen.add(key)
                links.append(Link(target_id=target_id, link_type="linksTo"))
            continue

        resolved_type = link_type or "linksTo"
        resolved_label = label if link_type else None
        key = (target_id, resolved_type, resolved_label)
        if key not in seen:
            seen.add(key)
            links.append(Link(
                target_id=target_id,
                link_type=resolved_type,
                label=resolved_label,
            ))
    return ParseResult(
        links=tuple(links),
        ambiguous=tuple(ambiguous),
        malformed=tuple(malformed),
    )
