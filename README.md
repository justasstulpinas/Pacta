PACTA API

Backend API for contract template creation with open link signing, backend can generate HTML, DOCX, PDF files from signed contracts, user must be legged in to send a request.

STACK

FastAPI
SQLAlchemy
SQLite (`pacta.db`)
Pydantic
WeasyPrint (PDF generation)
python-docx + BeautifulSoup (DOCX generation)

REQUIRIMENTS

Python 3.11+ (tested with Python 3.13.7)
`pip`

SETUP

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
LAUNCH

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API URLS:

Swagger UI: `http://127.0.0.1:8000/docs`
ReDoc: `http://127.0.0.1:8000/redoc`
Health check: `http://127.0.0.1:8000/health`
NOTES

App creates tables automatically on startup.
SQLite database file is stored at `./pacta.db`.
User profile avatars are stored in `app/uploads/`.
