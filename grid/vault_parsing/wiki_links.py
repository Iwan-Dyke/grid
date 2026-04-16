import re
from dataclasses import dataclass

from grid.note_modeling import Link

WIKI_LINK_PATTERN = re.compile(r"\[\[(?:(\w+)::)?(\d{14})(?:\|(.+?))?\]\]")


@dataclass(frozen=True)
class AmbiguousLink:
    target_id: str
    label: str
    raw: str


@dataclass(frozen=True)
class ParseResult:
    links: list[Link]
    ambiguous: list[AmbiguousLink]


def extract_wiki_links(body: str) -> ParseResult:
    seen = set()
    links = []
    ambiguous = []
    for match in WIKI_LINK_PATTERN.finditer(body):
        link_type = match.group(1)
        target_id = match.group(2)
        label = match.group(3)

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
    return ParseResult(links=links, ambiguous=ambiguous)
