from app.services.placeholder_service import PlaceholderService
from app.services.placeholder_service import PlaceholderService
from app.core.exceptions import ValidationError
import pytest


def test_validate_exact_match():
    fields = ["name", "surname"]
    payload = {"name": "John", "surname": "Doe"}
    PlaceholderService.validate_payload(fields, payload)


def test_validate_missing():
    fields = ["name", "surname"]
    payload = {"name": "John"}

    with pytest.raises(ValidationError):
        PlaceholderService.validate_payload(fields, payload)


def test_validate_extra():
    fields = ["name"]
    payload = {"name": "John", "age": "30"}

    with pytest.raises(ValidationError):
        PlaceholderService.validate_payload(fields, payload)


def test_validate_missing_and_extra():
    fields = ["name", "surname"]
    payload = {"name": "John", "age": "30"}

    with pytest.raises(ValidationError):
        PlaceholderService.validate_payload(fields, payload)



def test_extract_basic():
    content = "Hello {{name}} from {{company}}"
    result = PlaceholderService.extract_placeholders(content)
    assert result == ["company", "name"]


def test_extract_with_spaces():
    content = "Hello {{  name  }} and {{   surname }}"
    result = PlaceholderService.extract_placeholders(content)
    assert result == ["name", "surname"]


def test_duplicate_placeholders():
    content = "Hello {{name}} and {{name}}"
    result = PlaceholderService.extract_placeholders(content)
    assert result == ["name"]


def test_no_placeholders():
    content = "Hello world"
    result = PlaceholderService.extract_placeholders(content)
    assert result == []


def test_invalid_names_not_captured():
    content = "Hello {{ 123name }} {{ name! }}"
    result = PlaceholderService.extract_placeholders(content)
    assert result == []
