import re

from grid.note_modeling import Link

WIKI_LINK_PATTERN = re.compile(r"\[\[(?:(\w+)::)?(\d{14})(?:\|(.+?))?\]\]")


def extract_wiki_links(body: str) -> list[Link]:
    seen = set()
    links = []
    for match in WIKI_LINK_PATTERN.finditer(body):
        link_type = match.group(1) or "linksTo"
        target_id = match.group(2)
        label = match.group(3) if match.group(1) else None
        key = (target_id, link_type, label)
        if key not in seen:
            seen.add(key)
            links.append(Link(target_id=target_id, link_type=link_type, label=label))
    return links
