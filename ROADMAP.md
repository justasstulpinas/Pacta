# Pacta — Launch Roadmap

## Phase 1 — Fix What's Broken (1–2 days)
*The app doesn't fully work yet. These must be done first.*

- [x] Call `seed_rbac(db)` at startup in `app/main.py` — roles never get created
- [x] Seed the `admin:all` permission and assign it to the `admin` role in `app/core/seed.py`
- [x] Register `BadRequestError` exception handler in `app/main.py` — currently causes 500 on submission confirm
- [x] Move `SECRET_KEY` to an environment variable (`.env` file + `python-dotenv`)
- [x] Move `DATABASE_URL` to an environment variable
- [x] Guard `request.client` against `None` in `app/routers/links.py`
- [x] Remove `print("TABLES:", ...)` from `app/main.py`

---

## Phase 2 — Security Hardening (2–3 days)
*Required before any public traffic.*

- [x] Sanitize template content before rendering HTML (use `bleach` or similar to strip `<script>`, event handlers)
- [x] Add rate limiting to `POST /links/public/{token}/submit` (use `slowapi`)
- [x] Validate avatar file magic bytes, not just declared content-type
- [x] Set `ACCESS_TOKEN_EXPIRE_MINUTES` from environment variable
- [x] Add HTTPS redirect middleware for production
- [x] Lock CORS `allow_origins` to actual frontend domain (not just localhost) via env var
- [x] Add a link revocation endpoint `DELETE /links/{link_id}` so owners can cancel a live link

---

## Phase 3 — Replace the Schema Hack with Proper Migrations (1 day)
*Required before you have real user data you can't afford to lose.*

- [x] Install and configure Alembic
- [x] Generate initial migration from current models
- [x] Delete `_ensure_schema_compatibility()` from `app/main.py`
- [x] Document migration workflow in README

---

## Phase 4 — Complete the Core Submission Flow (3–5 days)
*The contract lifecycle is half-built.*

- [x] Add `POST /contracts/submissions/{id}/cancel` endpoint (set status → `cancelled`)
- [x] Add `POST /contracts/submissions/{id}/complete` endpoint (set status → `completed`)
- [x] Add `DELETE /contacts/{contact_id}` endpoint
- [x] Replace `ContractTemplateOut` on the list endpoint with `ContractTemplateListItem` (don't return full content on list)
- [x] Add pagination (`limit`/`offset`) to templates list and contacts list
- [x] Add template search/filter by `status` and `name` query params
- [x] Fix conftest: remove duplicate `user`/`test_user` fixtures

---

## Phase 5 — E-Signature (1–2 weeks)
*The single biggest gap between a demo and a sellable product.*

Choose one approach:

**Option A — Simple (draw or type signature, stored as image):**
- [x] Add `signature_image` field to `FilledContract` (base64 PNG)
- [x] Add `{{signature}}` as a reserved placeholder type
- [x] Frontend captures signature (draw pad or typed name rendered as image)
- [x] Store signature image with the submission
- [x] Embed signature image in PDF/DOCX export

**Option B — Third-party legal e-sign (recommended for selling to businesses):**
- [ ] Integrate DocuSign, HelloSign (Dropbox Sign), or Adobe Sign API
- [ ] When a submission is confirmed, trigger a signing ceremony via API
- [ ] Store the signed document URL/reference back on the `FilledContract`
- [ ] Webhook from the e-sign provider updates submission status to `completed`

---

## Phase 6 — Email Notifications (2–3 days)
*Users need to know when things happen.*

- [x] Choose email provider: Resend, SendGrid, or AWS SES
- [x] Send email to template owner when a new submission arrives
- [x] Send email to submitter confirming their submission was received (requires capturing submitter email during submit)
- [x] Send email to submitter when their submission is confirmed
- [x] Add `submitter_email` field to `FilledContract` (or capture from payload)
- [x] Email verification on registration
- [x] Forgot password / reset password full flow with email
- [x] Improve email copy — unified to Lithuanian, professional tone
- [x] Owner notification email must include a direct link to view the submission in the app
- [x] Submitter confirmation email must include a download link for the signed PDF

---

## Phase 7 — Frontend (2–4 weeks if building yourself)
*Next.js frontend is in progress.*

- [x] Auth flow: register, login, logout, token refresh
- [x] Template editor with placeholder hint UI (`{{field_name}}` helper)
- [x] Template list with status badges and lifecycle actions (activate, archive, delete)
- [x] Public link generator with prefill form for `owner_*` fields
- [x] Shareable link page: template viewer + public submit form
- [x] Submission inbox per template with status filtering
- [x] Submission detail view with confirm/cancel actions
- [x] One-click PDF and DOCX download
- [x] Profile page with avatar upload
- [x] Contact list management
- [x] Owner signature field (`{{user_signature}}`) — stored on profile, embedded inline in documents
- [ ] Mobile-friendly signing and contract review page (clients sign on phone)

---

## Phase 8 — Billing & Multi-Tenancy (1–2 weeks)
*Required to sell the product.*

- [x] **Logo on documents:** Upload company logo to profile, freely drag position on A4 preview, embedded at chosen position on every PDF page via `position:fixed`.
- [ ] Integrate Stripe (subscriptions)
- [ ] Define plans: e.g. Free (3 templates, 10 submissions/month), Pro (unlimited), Business (team + API access)
- [ ] Add `Plan` / `Subscription` model to track per-user limits
- [ ] Enforce limits in services (template create, link create, submissions)
- [ ] Stripe webhook handler for `invoice.paid`, `customer.subscription.deleted`
- [ ] Billing portal page in frontend

---

## Phase 9 — Observability & Ops (3–5 days)
*You need to know when things break in production.*

- [x] Replace `print()` calls with structured logging (`structlog` or Python `logging`)
- [ ] Add request ID to each request (middleware)
- [ ] Integrate Sentry for error tracking
- [x] Add a real health check endpoint that pings the DB (not just `{"health": "alive"}`)
- [x] Switch from SQLite to PostgreSQL for production (update `DATABASE_URL`, drop `check_same_thread`)
- [ ] Containerize with Docker + `docker-compose` (app + db)
- [ ] Set up CI: run `pytest` on every push (GitHub Actions)

---

## Phase 10 — Launch Prep (3–5 days)

- [ ] Write a proper README with screenshots and a 60-second setup guide
- [ ] Add API documentation notes for each endpoint (FastAPI `summary=` and `description=`)
- [ ] Create a Terms of Service and Privacy Policy (required to charge money)
- [x] Set up a production domain with SSL (Vercel/Railway/Render/Fly.io)
- [ ] Seed a demo account with example templates for new users
- [ ] Smoke-test the full flow end-to-end on production before announcing

---

## v1.1 — Post-Launch Additions

Features to build after the initial launch, once real users are in the product.

- [x] **vCard export** — "Eksportuoti kontaktą" button on contact page, downloads a `.vcf` file that works with iOS/Android address book and Google Contacts import (~2h)
- [ ] **Google Contacts sync** — via Google People API, requires OAuth2 per user (~2–3 days)
- [ ] **Template search/filter** — filter by status and name on the templates list
- [ ] **DOCX import (Pro)** — user uploads existing `.docx` contract, backend converts to HTML via python-docx, loads into editor. User manually adds `{{placeholders}}`. `.docx` only, no `.doc` support. (~3–4 days)

---

## Suggested Order If Solo

```
Phase 1 → 2 → 3 → 5 (Option A) → 6 → 7 → Phase 4 (in parallel with 7) → 9 → 8 → 10
```

The backend is architecturally sound and the frontend is essentially feature-complete.
Phases 1–3 are fully done. Phase 5 (e-signature Option A) and Phase 6 (email) are largely
done with only polish remaining. Phase 7 (frontend) is complete.

You're roughly 60–65% of the way to a shippable product. The remaining bets are:

1. **Phase 4** — cancel/complete endpoints, pagination, contact deletion. Small but needed.
2. **Billing** (Phase 8) — required to charge money, 1–2 weeks of work.
3. **Observability** (Phase 9) — Sentry + structured logging, needed to know when things break.
4. **Launch prep** (Phase 10) — ToS, Privacy Policy, demo account, README.

The product is demo-ready today and production-safe (PostgreSQL is live on Railway).
