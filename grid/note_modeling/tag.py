from dataclasses import dataclass

MAX_TAG_LENGTH = 50


@dataclass(frozen=True)
class Tag:
    name: str

    def __post_init__(self):
        stripped = self.name.strip()
        if not stripped:
            raise ValueError("Tag name cannot be empty")
        if any(c.isspace() for c in stripped):
            raise ValueError("Tag name cannot contain whitespace")
        if len(stripped) > MAX_TAG_LENGTH:
            raise ValueError(f"Tag name cannot exceed {MAX_TAG_LENGTH} characters")
        object.__setattr__(self, "name", stripped.lower())
