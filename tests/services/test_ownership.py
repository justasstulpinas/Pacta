import pytest
from app.services.ownership import require_ownership
from app.core.exceptions import ForbiddenError

def test_require_ownership_forbidden():
    with pytest.raises(ForbiddenError):
        require_ownership(resource_owner_id=1, user_id=2)

def test_require_ownership_ok():
    require_ownership(resource_owner_id=1, user_id=1)
