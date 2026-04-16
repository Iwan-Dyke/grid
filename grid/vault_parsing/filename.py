from slugify import slugify


def generate_filename(note_id: str, title: str) -> str:
    return f"{note_id}-{slugify(title)}.md"
