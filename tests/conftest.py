import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from app.core.exceptions import ForbiddenError
from tests.api.test_authorization_dependency import router


@pytest.fixture
def client():
    app = FastAPI()

    @app.exception_handler(ForbiddenError)
    def forbidden_handler(_, __):
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})

    app.include_router(router)

    return TestClient(app)
