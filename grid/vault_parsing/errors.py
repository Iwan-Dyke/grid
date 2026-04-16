class GridError(Exception):
    pass


class NoteNotFoundError(GridError):
    pass


class NoteParseError(GridError):
    pass
