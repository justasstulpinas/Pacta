import re
from typing import List
from typing import Dict, List
from app.core.exceptions import ValidationError


PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*(?P<field>[a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")

class PlaceholderService:
    @staticmethod
    def extract_placeholders(content: str) -> List[str]:  
        matches = PLACEHOLDER_PATTERN.finditer(content)
        fields= {match.group("field") for match in matches}
        return sorted(fields)
    
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
                    "missing fields": sorted(missing),
                    "extra fields": sorted(extra)
                }
            )
    @staticmethod
    def render_content(content: str, payload: dict) -> str:
        def replace(match):
            field = match.group("field")
            return str(payload.get(field, ""))

        return PLACEHOLDER_PATTERN.sub(replace, content)
        