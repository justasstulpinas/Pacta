# Launch Plan — 4 Months to Full Launch

**Schedule:** 4 sessions/week (Mon × 2, Tue × 2) · 1–2 hours each · ~64 sessions total  
**Target:** Spotless, production-ready, monetised, self-hosted app  
**Core flow:** Register → Create template → Send link → Client signs (eIDAS) → PDF downloaded → Owner downloads via email  
**Additional scope:** Full super admin, Stripe billing + plan gates, Mac Mini self-hosting

Mark sessions with ✅ when done.

---

## Month 1 — Foundation: Security + Core Flow

### Week 1 — Secrets & Auth Hardening
Critical first. Nothing else is safe until this is done.

| # | Session | Task | Est |
|---|---------|------|-----|
| 1 | Mon | **Purge git history of secrets.** Use `git filter-repo` to scrub `.env` from all commits. Rotate `SECRET_KEY` and `RESEND_API_KEY` afterward. | 1h |
| 2 | Mon | **Security headers middleware.** Add `CSP`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin`, `Permissions-Policy` to every response via FastAPI middleware. | 1h |
| 3 | Tue | **Rate limit login + lockout.** Add slowapi limit to `POST /auth/login` (10/min per IP). Add account lockout after 10 failed attempts (15 min lockout, stored in DB). | 1h |
| 4 | Tue | **Audit all route auth guards.** Walk every router file — confirm every authenticated endpoint has `get_current_user` dependency. Check that owners can only see their own templates/submissions. | 1h |

### Week 2 — Input Validation & API Hygiene
| # | Session | Task | Est |
|---|---------|------|-----|
| 5 | Mon | **Add max-length to all Pydantic schemas.** Template name ≤ 200 chars, content ≤ 500k chars, email ≤ 254 chars, passwords 8–128 chars. Add to every schema file. | 1h |
| 6 | Mon | **Trim API responses.** Audit what each endpoint returns — remove internal IDs, hashes, and fields clients don't need. Check `FilledContractResponse`, `TemplateOut`, `PublicLinkOut`. | 1h |
| 7 | Tue | **Dependency security scan.** Run `pip-audit` on requirements.txt. Update any package with a known CVE. Document any that can't be updated and why. | 1h |
| 8 | Tue | **Force HTTPS + tighten CORS.** In production: `HTTPSRedirectMiddleware` on. CORS `allow_origins` must only contain the exact Vercel frontend URL — no wildcards. Verify Railway sets correct headers. | 1h |

### Week 3 — Signing Flow Polish (Client Experience)
The most user-facing flow. Must be perfect.

| # | Session | Task | Est |
|---|---------|------|-----|
| 9 | Mon | **Signing page — mobile layout audit.** Open `/sign/[uuid]` on a phone. Fix: code input keyboard type, preview scroll on small screens, form fields cramped, signature pad touch response. | 2h |
| 10 | Mon | **Signing page — consent step copy.** Rewrite the two checkbox labels in proper Lithuanian legal language. Add a one-liner about what electronic signature means legally. | 1h |
| 11 | Tue | **Signing page — error states.** Test: expired link, already signed link, wrong code 5× lockout, network failure mid-sign. Each should show a clear, non-technical error screen. | 1h |
| 12 | Tue | **Signing success screen.** Add: "Sutartis pasirašyta ✓ · Kopija atsisiųsta į jūsų įrenginį · Savininkas informuotas." Make it feel final and trustworthy, not like a generic success toast. | 1h |

### Week 4 — Sharing Flow Polish (Owner Experience)
| # | Session | Task | Est |
|---|---------|------|-----|
| 13 | Mon | **Link generation page — simplify.** Too many steps currently. One screen: fill owner fields → set expiry → optional client email → Generate. Show URL + code in one box with a "Copy both" button. | 2h |
| 14 | Mon | **Owner download page — UX.** `/download/owner/[uuid]` — better warning that it's one-time, clearer code entry label, handle "already downloaded" and "expired" states with helpful copy. | 1h |
| 15 | Tue | **Contracts dashboard — secure submissions section.** Status badges for pending/signed/completed/declined. "Signed" row shows "📧 Check your email to download" with the email address it was sent to. | 1h |
| 16 | Tue | **New Contract modal — fix and simplify.** Test the full flow from the modal: template selection, owner fields, generate, code display. Remove confusing "or" divider if email not yet sent. | 1h |

---

## Month 2 — Polish: Auth, Editor, Dashboard, Landing Page

### Week 5 — Auth Flows
Every auth page must be clean and handle all edge cases.

| # | Session | Task | Est |
|---|---------|------|-----|
| 17 | Mon | **Login page.** Better error messages ("Neteisingas el. paštas arba slaptažodis" not "Invalid credentials"). Lockout feedback ("Paskyra laikinai užblokuota. Bandykite po 15 min."). Loading state on button. | 1h |
| 18 | Mon | **Register page.** Password strength meter (weak/medium/strong). Real-time validation on email format. Clear "Check your inbox" screen after register with resend button. | 1h |
| 19 | Tue | **Email verification flow.** `/verify-email` — handle expired token, already verified, invalid token. Add a "Resend verification email" link. Success screen should redirect to dashboard. | 1h |
| 20 | Tue | **Forgot password + reset flow.** End-to-end test. Reset link expiry must show clear message. Password mismatch error. Redirect to login on success with "Slaptažodis pakeistas" toast. | 1h |

### Week 6 — Template Editor
| # | Session | Task | Est |
|---|---------|------|-----|
| 21 | Mon | **DOCX import UX.** Test with 5 real contract DOCX files. Fix: formatting loss, broken paragraphs, tables, bold/italic. Show a "before/after" diff or preview. Add clear error if file is too large or wrong format. | 2h |
| 22 | Mon | **Placeholder sidebar.** When user types `{{`, autocomplete shows available placeholder types (client_, owner_, sys_). Clicking inserts it. Makes template creation 10× easier. | 2h |
| 23 | Tue | **Template list page.** Empty state ("Dar neturite šablonų — sukurkite pirmąjį"). Status filter (draft/active/archived). Search by name. Each row shows placeholder count. | 1h |
| 24 | Tue | **Template save/publish flow.** "Save as draft" vs "Publish" — clear distinction. Warn before archiving if active links exist. Duplicate template option (already exists, just make it visible). | 1h |

### Week 7 — Dashboard & Navigation
| # | Session | Task | Est |
|---|---------|------|-----|
| 25 | Mon | **Dashboard home page.** Replace generic page with: count of pending signatures, count of signed this month, quick-action buttons ("New template", "Send contract"). No charts needed — just numbers. | 1h |
| 26 | Mon | **Sidebar navigation.** Review all items: Templates, Sutartys (contracts), Kontaktai, Nustatymai. Add badge count on Sutartys for "pending" items. Mobile hamburger menu. | 1h |
| 27 | Tue | **Settings page.** Profile info, signature upload, logo upload — all in one scrollable page. Fix: logo/signature preview doesn't refresh after upload. Add "Delete" option next to each. | 1h |
| 28 | Tue | **Error pages — 404, 403, suspended.** Custom pages with Melno branding and a "← Grįžti" link. Suspended page must explain what happened and how to contact. No default Next.js error pages. | 1h |

### Week 8 — Landing Page Part 1: Structure + Hero
Your own design — not AI-generated generic layout.

| # | Session | Task | Est |
|---|---------|------|-----|
| 29 | Mon | **Landing page architecture.** Decide on sections, scrolling behavior, font choice. Write real headline and subheadline in Lithuanian. Sketch the hero layout (paper/Figma, not code). | 1h |
| 30 | Mon | **Hero section — code.** Implement the hero: headline, subheadline, primary CTA ("Pradėti nemokamai"), secondary CTA ("Peržiūrėti demo"). Background treatment. Navigation bar. | 2h |
| 31 | Tue | **How it works section.** 3-step flow: "Sukurkite šabloną → Išsiųskite nuorodą → Klientas pasirašo". Use icons or minimal illustration. Keep it under 200 words total. | 2h |
| 32 | Tue | **Features section.** 4 key features: eIDAS signature, no PDF emailed, GDPR compliant, Lithuanian-first. Each has a short heading + 1-sentence description. No bullet soup. | 1h |

---

## Month 3 — Hardening: Landing Page, Emails, Perf, Launch

### Week 9 — Landing Page Part 2: Trust + Legal
| # | Session | Task | Est |
|---|---------|------|-----|
| 33 | Mon | **Social proof + pricing section.** "Early access — nemokama" or first pricing tier. Even one real testimonial quote from a test user is better than nothing. "Naudoja X įmonių" when you have the number. | 2h |
| 34 | Mon | **Footer + navigation.** All legal links: Privatumo politika, Naudojimo sąlygos, Kontaktai. Social links. Copyright. Navigation links to all landing sections. | 1h |
| 35 | Tue | **Privacy Policy page** (`/privatumo-politika`). Lithuanian. Covers: what data is collected, what is NOT stored (client IDs), retention periods, right to erasure, GDPR contact. | 2h |
| 36 | Tue | **Terms of Service page** (`/naudojimo-salygos`). Lithuanian. Covers: scope of service, electronic signature legal basis (eIDAS), limitation of liability, account termination. | 2h |

### Week 10 — Email Redesign
| # | Session | Task | Est |
|---|---------|------|-----|
| 37 | Mon | **Redesign signing invitation email.** The client receives this first — it must feel trustworthy. Melno branding, clear sender name, prominent 6-digit code, no clutter. Test on Gmail + Outlook. | 2h |
| 38 | Mon | **Redesign owner notification email.** Sent when client signs. Must convey urgency (one-time download). Download code prominent. Link clearly labeled as one-time. | 1h |
| 39 | Tue | **Redesign remaining emails.** Submission confirmation, contract declined, password reset, email verification — consistent Melno template, proper Lithuanian, test delivery via Resend domain. | 2h |
| 40 | Tue | **Verify custom domain email.** `noreply@melno.app` must be fully verified on Resend. SPF + DKIM records set. Test delivery to Gmail, Apple Mail, Outlook. Check spam score. | 1h |

### Week 11 — Performance & Production
| # | Session | Task | Est |
|---|---------|------|-----|
| 41 | Mon | **GZip + response compression.** Add `GZipMiddleware` to FastAPI. Verify JSON responses are compressed. Check Time-to-First-Byte on Railway. | 30m |
| 42 | Mon | **Database: add indexes + PostgreSQL switch.** Add indexes on `submissions.creator_id`, `submissions.status`, `filled_contracts.template_id`. Switch `DATABASE_URL` to PostgreSQL on Railway. Run migrations. | 2h |
| 43 | Tue | **Production deployment checklist.** All env vars set on Railway + Vercel. HTTPS enforced. Health check endpoint working. Error monitoring (Sentry free tier — takes 30 min to add). | 1h |
| 44 | Tue | **Browser compatibility pass.** Test full signing flow on: Safari (iPhone), Chrome (Android), Firefox. Fix anything that breaks. Focus on: signature pad, date inputs, cookie behavior. | 2h |

### Week 12 — Launch
| # | Session | Task | Est |
|---|---------|------|-----|
| 45 | Mon | **End-to-end production test.** With real accounts on production. Full flow: register → verify email → create template → send link → sign on phone → owner download. No localhost. | 2h |
| 46 | Mon | **Soft launch.** Invite 3–5 real users (colleagues, clients). Give them a template and ask them to sign. Watch what breaks. Take notes. | 1h |
| 47 | Tue | **Fix top 3 bugs from soft launch feedback.** | 2h |
| 48 | Tue | **Buffer.** Fix anything unexpected. Or: start on post-launch feature (contacts sync, billing integration). | 2h |

---

## Hard Rules

- **Never deploy with secrets in git.** Week 1 Session 1 is non-negotiable.
- **Mobile first.** Every page must work on a 390px screen before you're done with it.
- **Lithuanian everywhere.** No English strings visible to end users.
- **One session = one task.** Don't start the next until the current one is done and tested.
- **If a session runs over 2 hours, stop and split it.** Scope creep will kill the schedule.

---

## Known Debt (Do Not Forget)

- `app/services/contract_submission_service.py` is legacy and returns 400 on all calls — the old dashboard download buttons will fail for any legacy `FilledContract`. Fix in Week 4 or Week 7.
- `signature_image` is stored on the `Submission` model for audit purposes — confirm this is acceptable under your privacy policy before launch.
- The `pacta.db` SQLite file must be replaced with PostgreSQL before launch (Week 11). SQLite will lose data if Railway restarts.
- Old `PublicLink` / `FilledContract` records in the DB have no sensitive data (columns dropped) but the rows still exist — decide whether to keep or purge before launch.
- Owner download frontend page (`/download/owner/[uuid]`) works but has no `/dashboard` link in nav — add it in Week 4.

---

## Month 4 — Admin, Billing & Self-Hosting

### Week 13 — Stripe Billing: Backend

| # | Session | Task | Est |
|---|---------|------|-----|
| 49 | Mon | **Add plan field to User model.** New column: `plan` enum (`free`, `pro`), default `free`. Migration. Add `stripe_customer_id` column. `pip install stripe`. | 1h |
| 50 | Mon | **Stripe products + prices setup.** Create products in Stripe dashboard (Free, Pro). Store price IDs in `.env`. Write `POST /billing/create-checkout-session` endpoint — creates Stripe Checkout for the logged-in user. | 2h |
| 51 | Tue | **Stripe webhook endpoint.** `POST /billing/webhook` — handle `checkout.session.completed`, `customer.subscription.deleted`, `invoice.payment_failed`. Update `user.plan` in DB accordingly. Verify with Stripe CLI. | 2h |
| 52 | Tue | **Feature gates.** Free: max 3 active templates, max 5 submissions/month. Add `PlanService.check_template_limit(user)` and `check_submission_limit(user)`. Raise `ForbiddenError` with upgrade message when exceeded. | 1h |

### Week 14 — Stripe Billing: Frontend

| # | Session | Task | Est |
|---|---------|------|-----|
| 53 | Mon | **Upgrade page** (`/dashboard/billing`). Shows current plan (Free/Pro), usage bars (templates: X/3 used, submissions: X/5 used), Pro features list, "Pereiti prie Pro — €8/mėn" button → Stripe Checkout. | 2h |
| 54 | Mon | **Billing success + cancel pages.** Success: "Pro planas aktyvuotas ✓" — usage limits disappear, email invitations unlocked. Cancel: back link, no pressure copy. Nav shows "Pro" badge after upgrade. | 1h |
| 55 | Tue | **Inline upgrade prompts.** Three trigger points: (1) creating 4th template, (2) 6th submission in month, (3) trying to send email invitation on free plan. Each shows a small banner — not a modal — with upgrade link. | 1h |
| 56 | Tue | **Stripe customer portal link.** Billing page: "Valdyti prenumeratą →" → `POST /billing/portal-session` → Stripe-hosted portal (cancel, update card, see invoices). No custom cancel flow needed. | 1h |

### Week 15 — Super Admin Panel

| # | Session | Task | Est |
|---|---------|------|-----|
| 57 | Mon | **Admin: users table upgrade.** Add `plan` column, `stripe_customer_id` column, `submissions_this_month` count. Show plan badge (Free/Pro) on each row. Search by email. | 1h |
| 58 | Mon | **Admin: manual plan toggle.** Per-user "Set plan" dropdown (Free / Pro) with a reason text field. Writes to DB directly, bypasses Stripe (for gifting, partnerships, testing). Adds entry to audit log. | 1h |
| 59 | Tue | **Admin: plan audit log.** New table `plan_changes` — who changed what plan, when, reason. Show last 5 changes per user in the user row expansion. This is your paper trail for manual overrides. | 1h |
| 60 | Tue | **Admin: system stats page.** DB size, total users by plan, submissions today/week/month, server uptime, last deployment time. Read-only. Refresh button. No charts needed — just numbers in a grid. | 1h |

### Week 16 — Mac Mini Self-Hosting (Cloudflare Tunnel, full stack)

Both backend (FastAPI) and frontend (Next.js) run on the Mini. Cloudflare Tunnel routes both domains. No Vercel, no Railway, no static IP, no certbot.

| # | Session | Task | Est |
|---|---------|------|-----|
| 61 | Mon | **Mac Mini base setup.** Install via Homebrew: PostgreSQL 16, Python 3.13, Node.js 20. Create dedicated `pacta` user. Clone both repos. Backend: venv + `pip install -r requirements.txt` + `.env`. Frontend: `npm install` + `.env.local` (`NEXT_PUBLIC_API_URL=https://api.melno.app`). Both apps start manually — confirm no errors. | 2h |
| 62 | Mon | **Cloudflare Tunnel — both domains.** Install `cloudflared`. Create one tunnel with two ingress rules in `config.yml`: `melno.app → localhost:3000` and `api.melno.app → localhost:8000`. Add both CNAMEs in Cloudflare DNS. Test: `https://melno.app` loads Next.js, `https://api.melno.app/health` returns OK. SSL automatic. | 1h |
| 63 | Tue | **Process management (3 LaunchAgents).** Three `~/Library/LaunchAgents` plists: uvicorn (port 8000, 2 workers), `next start` (port 3000), cloudflared. All auto-start on boot, restart on crash. Logs to `~/Library/Logs/pacta/`. Test: reboot Mac Mini, all three come up automatically. | 1h |
| 64 | Tue | **Backups + deploy script.** Hourly `pg_dump` to external drive via cron. Single `deploy.sh` script that handles both repos: `git pull` (both) → `pip install` → `npm install` → `npm run build` → `alembic upgrade head` → `launchctl kickstart` (uvicorn + next). One command for a full deploy. | 2h |

---

## Stripe Plan Design — DECIDED

| | Free | Pro |
|--|------|-----|
| Active templates | 3 | Unlimited |
| Submissions/month | 5 | Unlimited |
| eIDAS signing | ✓ | ✓ |
| Custom logo/signature | ✓ | ✓ |
| Email invitations (send code automatically) | ✗ | ✓ |
| Priority support | ✗ | ✓ |
| Price | €0 | **€8/month** |

**Annual discount:** €6.50/month (€78/year) — optional, add later.  
Stripe price ID goes in `.env` as `STRIPE_PRO_PRICE_ID`.  
Stripe webhook secret goes in `.env` as `STRIPE_WEBHOOK_SECRET`.

### What changes between plans in the UI

**Free user sees:**
- Usage bar on dashboard: "3/5 sutartys šį mėnesį · 1/3 šablonų"
- "Pro" lock icon on "Siųsti el. paštu" button in link generation
- Inline banner when creating 4th template or 6th submission
- No upgrade nag anywhere else — don't be annoying

**Pro user sees:**
- No usage bars, no lock icons, no banners
- Small "Pro" badge in the sidebar next to their name
- "Valdyti prenumeratą →" link in settings

---

## Mac Mini Architecture (Cloudflare Tunnel, full stack)

```
Internet
  ↓
Cloudflare (SSL, DDoS — free)
  ↓
cloudflared tunnel (one tunnel, two ingress rules)
  ├── melno.app      → localhost:3000  (Next.js)
  └── api.melno.app  → localhost:8000  (FastAPI)

Mac Mini
  ├── next start          (port 3000)
  ├── uvicorn app.main:app (port 8000, 2 workers)
  └── PostgreSQL 16        (port 5432, local only)
```

No Vercel. No Railway. No nginx. No certbot. No static IP.  
Everything runs on one machine behind one Cloudflare tunnel.  
Frontend `.env.local`: `NEXT_PUBLIC_API_URL=https://api.melno.app`  
Backend `.env`: `FRONT_END_URL=https://melno.app`, `APP_URL=https://melno.app`
