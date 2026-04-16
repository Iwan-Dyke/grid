import pytest
from unittest.mock import patch
from datetime import datetime, UTC

from grid.note_modeling.identifiers import validate_note_id, generate_note_id


class TestValidateNoteId:
    def test_accepts_14_digits(self):
        validate_note_id("20260409221400")

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            validate_note_id("")

    def test_rejects_non_numeric(self):
        with pytest.raises(ValueError):
            validate_note_id("not-an-id")

    def test_rejects_short(self):
        with pytest.raises(ValueError):
            validate_note_id("2026040922140")

    def test_rejects_long(self):
        with pytest.raises(ValueError):
            validate_note_id("202604092214001")


class TestGenerateNoteId:
    def test_returns_14_digit_string(self):
        result = generate_note_id()
        assert len(result) == 14
        assert result.isdigit()

    def test_uses_utc(self):
        fixed = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)
        with patch("grid.note_modeling.identifiers.datetime") as mock_dt:
            mock_dt.now.return_value = fixed
            mock_dt.UTC = UTC
            assert generate_note_id() == "20260409221400"
