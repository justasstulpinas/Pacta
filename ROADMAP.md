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
- [ ] Add HTTPS redirect middleware for production
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

- [ ] Add `POST /contracts/submissions/{id}/cancel` endpoint (set status → `cancelled`)
- [ ] Add `POST /contracts/submissions/{id}/complete` endpoint (set status → `completed`)
- [ ] Add `DELETE /contacts/{contact_id}` endpoint
- [ ] Replace `ContractTemplateOut` on the list endpoint with `ContractTemplateListItem` (don't return full content on list)
- [ ] Add pagination (`limit`/`offset`) to templates list and contacts list
- [ ] Add template search/filter by `status` and `name` query params
- [ ] Fix conftest: remove duplicate `user`/`test_user` fixtures

---

## Phase 5 — E-Signature (1–2 weeks)
*The single biggest gap between a demo and a sellable product.*

Choose one approach:

**Option A — Simple (draw or type signature, stored as image):**
- [ ] Add `signature_image` field to `FilledContract` (base64 PNG)
- [ ] Add `{{signature}}` as a reserved placeholder type
- [ ] Frontend captures signature (draw pad or typed name rendered as image)
- [ ] Store signature image with the submission
- [ ] Embed signature image in PDF/DOCX export

**Option B — Third-party legal e-sign (recommended for selling to businesses):**
- [ ] Integrate DocuSign, HelloSign (Dropbox Sign), or Adobe Sign API
- [ ] When a submission is confirmed, trigger a signing ceremony via API
- [ ] Store the signed document URL/reference back on the `FilledContract`
- [ ] Webhook from the e-sign provider updates submission status to `completed`

---

## Phase 6 — Email Notifications (2–3 days)
*Users need to know when things happen.*

- [ ] Choose email provider: Resend, SendGrid, or AWS SES
- [ ] Send email to template owner when a new submission arrives
- [ ] Send email to submitter confirming their submission was received (requires capturing submitter email during submit)
- [ ] Send email to submitter when their submission is confirmed
- [ ] Add `submitter_email` field to `FilledContract` (or capture from payload)

---

## Phase 7 — Frontend (2–4 weeks if building yourself)
*Next.js frontend is in progress.*

- [ ] Auth flow: register, login, logout, token refresh
- [ ] Template editor with placeholder hint UI (`{{field_name}}` helper)
- [ ] Template list with status badges and lifecycle actions (activate, archive, delete)
- [ ] Public link generator with prefill form for `owner_*` fields
- [ ] Shareable link page: template viewer + public submit form
- [ ] Submission inbox per template with status filtering
- [ ] Submission detail view with confirm/cancel actions
- [ ] One-click PDF and DOCX download
- [ ] Profile page with avatar upload
- [ ] Contact list management

---

## Phase 8 — Billing & Multi-Tenancy (1–2 weeks)
*Required to sell the product.*

- [ ] Integrate Stripe (subscriptions)
- [ ] Define plans: e.g. Free (3 templates, 10 submissions/month), Pro (unlimited), Business (team + API access)
- [ ] Add `Plan` / `Subscription` model to track per-user limits
- [ ] Enforce limits in services (template create, link create, submissions)
- [ ] Stripe webhook handler for `invoice.paid`, `customer.subscription.deleted`
- [ ] Billing portal page in frontend

---

## Phase 9 — Observability & Ops (3–5 days)
*You need to know when things break in production.*

- [ ] Replace `print()` calls with structured logging (`structlog` or Python `logging`)
- [ ] Add request ID to each request (middleware)
- [ ] Integrate Sentry for error tracking
- [ ] Add a real health check endpoint that pings the DB (not just `{"health": "alive"}`)
- [ ] Switch from SQLite to PostgreSQL for production (update `DATABASE_URL`, drop `check_same_thread`)
- [ ] Containerize with Docker + `docker-compose` (app + db)
- [ ] Set up CI: run `pytest` on every push (GitHub Actions)

---

## Phase 10 — Launch Prep (3–5 days)

- [ ] Write a proper README with screenshots and a 60-second setup guide
- [ ] Add API documentation notes for each endpoint (FastAPI `summary=` and `description=`)
- [ ] Create a Terms of Service and Privacy Policy (required to charge money)
- [ ] Set up a production domain with SSL (Vercel/Railway/Render/Fly.io)
- [ ] Seed a demo account with example templates for new users
- [ ] Smoke-test the full flow end-to-end on production before announcing

---

## Suggested Order If Solo

```
Phase 1 → 2 → 3 → 5 (Option A) → 6 → 7 → Phase 4 (in parallel with 7) → 9 → 8 → 10
```

The backend is architecturally sound — the structure is clean and the hard design decisions
(versioning, snapshots, RBAC, placeholder engine) are already made. You're roughly 30–40%
of the way to a shippable product. The biggest remaining bets are e-signature, email,
frontend completion, and billing.
