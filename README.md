MELNO API

Backend API for contract template creation with open link signing, backend can generate HTML, DOCX, PDF files from signed contracts, user must be legged in to send a request.

STACK

FastAPI
SQLAlchemy
SQLite (`melno.db`)
Pydantic
WeasyPrint (PDF generation)
python-docx and  BeautifulSoup (DOCX generation)

REQUIRIMENTS

Python 3.11+ (built on python 3.13.7)
`pip`

SETUP

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

ALEMBIC
New migration:

```bash
alembic revision --autogenerate -m "description"
```
Apply migration:

```bash
alembic upgrade head
```
Roll back migration:

```bash
alembic downgrade -1
```

LAUNCH

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API URLS:

Swagger UI: `http://127.0.0.1:8000/docs`
Health check: `http://127.0.0.1:8000/health`
NOTES

App creates tables automatically on startup.
SQLite database file is stored at `./melno.db`.
