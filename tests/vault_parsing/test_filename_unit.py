from grid.vault_parsing.filename import generate_filename


class TestFilenameGeneration:
    def test_basic(self):
        assert generate_filename("20260409221400", "My Note Title") == "20260409221400-my-note-title.md"

    def test_lowercases(self):
        assert generate_filename("20260409221400", "ALL CAPS") == "20260409221400-all-caps.md"

    def test_non_ascii_transliterated(self):
        assert generate_filename("20260409221400", "Über Cool") == "20260409221400-uber-cool.md"

    def test_special_characters_stripped(self):
        result = generate_filename("20260409221400", "What's this & that?")
        assert result == "20260409221400-what-s-this-that.md"

    def test_multiple_spaces_collapsed(self):
        result = generate_filename("20260409221400", "Too   Many   Spaces")
        assert result == "20260409221400-too-many-spaces.md"

    def test_leading_trailing_whitespace(self):
        result = generate_filename("20260409221400", "  Padded Title  ")
        assert result == "20260409221400-padded-title.md"
