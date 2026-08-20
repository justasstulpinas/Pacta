import re
from typing import Dict, List
from app.core.exceptions import ValidationError

PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*(?P<field>[a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")

# Placeholders that contain personal identification data.
# Any template containing one of these triggers the eIDAS secure flow.
# Extend this set as new sensitive field types are required.
SENSITIVE_PLACEHOLDERS: frozenset[str] = frozenset({
    "client_ID",
    "passport",
    "personal_code",
    "identity_number",
    "driver_license",
})

class PlaceholderService:
    @staticmethod
    def extract_placeholders(content: str) -> List[str]:
        matches = PLACEHOLDER_PATTERN.finditer(content)
        fields = {match.group("field") for match in matches}
        return sorted(fields)

    @staticmethod
    def has_sensitive_fields(content: str) -> bool:
        """Return True if content contains any placeholder from SENSITIVE_PLACEHOLDERS."""
        fields = set(PlaceholderService.extract_placeholders(content))
        return bool(fields & SENSITIVE_PLACEHOLDERS)

    @staticmethod
    def classify_fields(fields: List[str]) -> tuple[List[str], List[str], List[str]]:
        owner_fields = sorted(field for field in fields if field.startswith("owner_"))
        system_fields = sorted(field for field in fields if field.startswith("sys_"))
        public_fields = sorted(
            field
            for field in fields
            if not field.startswith("owner_")
            and not field.startswith("sys_")
            and field not in PlaceholderService.RESERVED_FIELDS
        )
        return owner_fields, system_fields, public_fields

    @staticmethod
    def validate_owner_prefill(
        owner_fields: List[str],
        prefill: Dict[str, str],
    ) -> None:
        owner_set = set(owner_fields)
        provided_set = set(prefill.keys())
        missing = sorted(owner_set - provided_set)
        extra = sorted(provided_set - owner_set)
        if missing or extra:
            raise ValidationError(
                {
                    "missing_owner_fields": missing,
                    "extra_owner_fields": extra,
                }
            )
    
    @staticmethod
    def validate_payload(
        expected_fields: List[str],
        payload: Dict[str, str],
    ) -> None:
        
        expected_set= set(expected_fields)
        provided_set = set(payload.keys())

        missing = expected_set - provided_set
        extra = provided_set - expected_set

        if missing or extra:
            raise ValidationError(
                {
                    "missing_fields": sorted(missing),
                    "extra_fields": sorted(extra)
                }
            )
    RESERVED_FIELDS = {"signature", "user_signature"}

    @staticmethod
    def render_content(content: str, payload: Dict[str, str]) -> str:
        def replace(match):
            field = match.group("field")
            if field in PlaceholderService.RESERVED_FIELDS:
                return match.group(0)
            return str(payload.get(field, ""))

        return PLACEHOLDER_PATTERN.sub(replace, content)

    @staticmethod
    def render_selected_content(content: str, payload: Dict[str, str]) -> str:
        def replace(match):
            field = match.group("field")
            if field in payload:
                return str(payload[field])
            return match.group(0)

        return PLACEHOLDER_PATTERN.sub(replace, content)
        
