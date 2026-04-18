import re
from dataclasses import dataclass

MAX_TAG_LENGTH = 50
TAG_NAME_PATTERN = re.compile(r"^[a-z0-9_-]+$")


@dataclass(frozen=True)
class Tag:
    name: str

    def __post_init__(self):
        stripped = self.name.strip()
        if not stripped:
            raise ValueError("Tag name cannot be empty")
        if len(stripped) > MAX_TAG_LENGTH:
            raise ValueError(f"Tag name cannot exceed {MAX_TAG_LENGTH} characters")
        normalized = stripped.lower()
        if not TAG_NAME_PATTERN.match(normalized):
            raise ValueError(
                "Tag name must contain only lowercase letters, digits, hyphens, or underscores"
            )
        object.__setattr__(self, "name", normalized)
