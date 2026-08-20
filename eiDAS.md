# eIDAS SES — Implementation Roadmap

## What this is

A complete rewrite of the contract signing flow to comply with EU eIDAS Simple Electronic Signature (SES) requirements and GDPR data minimisation. Every submission — with or without a national ID — goes through the same secure flow. No client data is ever persisted to the database. No PDFs are emailed as attachments. No sequential integers appear in public URLs.

---

## Current state (what exists and what's wrong)

| Area | Current state | Problem |
|------|--------------|---------|
| `FilledContract.submitted_data` | JSON column with all client fields | Stores sensitive personal data permanently |
| `FilledContract.rendered_content` | Text column with full rendered HTML | Stores contract content with personal data |
| `FilledContractService.confirm_submission` | Emails PDF as attachment after owner confirmation | PDF travels through email servers |
| `GET /contracts/submissions/{id}` | Exposes sequential integer IDs | Enumerable — anyone can scrape all submissions |
| `POST /links/public/{token}/submit` | No access code required | Anyone with the token can sign |
| `PublicLink` | No recipient email field, no access code | Cannot email client directly or gate access |
| `send_contract_signed_pdf` | Attaches PDF to email | Violates "no attachment" requirement |
| Audit trail | None — only IP and user_agent on FilledContract | No eIDAS-compliant signing evidence |

---

## Target architecture

```
Owner creates submission
    ├── Option A: Generate link + 6-digit code (owner shares manually)
    └── Option B: Enter client email → system emails link + code

Client opens /sign/{uuid}
    → Enters 6-digit code (Argon2 verified, max 5 attempts)
    → Previews contract (read-only rendered HTML)
    → Can DECLINE here (email sent to owner)
    → Fills in personal data (name, surname, address, ID — ALL sensitive)
    → Draws or types signature
    → Checks two mandatory consent checkboxes
    → Clicks Sign
    → PDF renders in RAM
    → PDF streams directly to client as download (no storage)
    → Encrypted copy stored for owner (AES-256-GCM, key goes to owner only)
    → Audit trail written
    → Owner notified by email with download link + new 6-digit code

Owner opens /download/owner/{uuid}
    → Enters 6-digit code
    → PDF decrypted and streamed
    → Blob deleted, codes invalidated, submission marked completed
```

**No client data ever touches the database.**
**No PDF is ever sent as an email attachment.**
**No sequential integer is ever exposed in a public URL.**

---

## Dependencies to add

```
argon2-cffi          # Argon2 password hashing for verification codes
cryptography         # AES-256-GCM for temporary blob encryption
```

Add to `requirements.txt`.

---

## Phase 1 — New database models and migration

### 1.1 New model: `Submission`

File: `app/models/submission.py`

```python
class Submission(Base):
    __tablename__ = "submissions"

    # Public identifier — UUID4 only, never sequential int
    uuid = Column(String, primary_key=True, default=lambda: str(uuid4()))

    template_id          = Column(Integer, ForeignKey("contract_templates.id"), nullable=False)
    template_version_id  = Column(Integer, ForeignKey("contract_template_versions.id"), nullable=True)
    creator_id           = Column(Integer, ForeignKey("users.id"), nullable=False)

    recipient_email      = Column(String, nullable=True)   # set if owner sent via email
    is_sensitive         = Column(Boolean, default=False)  # True if template contains SENSITIVE_PLACEHOLDERS

    # Verification codes — Argon2 hashed, never plaintext
    access_code_hash          = Column(String, nullable=False)   # client uses to open signing page
    access_attempts           = Column(Integer, default=0)
    access_locked_until       = Column(DateTime, nullable=True)

    owner_download_code_hash  = Column(String, nullable=True)    # owner uses to download
    owner_download_attempts   = Column(Integer, default=0)
    owner_download_locked_until = Column(DateTime, nullable=True)

    # Encrypted PDF — AES-256-GCM. Key is NEVER stored here.
    # Key is embedded in owner's download URL only.
    encrypted_pdf_blob   = Column(LargeBinary, nullable=True)
    encryption_nonce     = Column(LargeBinary, nullable=True)   # GCM nonce

    # Status lifecycle
    status = Column(SAEnum(SubmissionStatus), default=SubmissionStatus.PENDING)

    # Timestamps
    created_at    = Column(DateTime, default=lambda: datetime.now(UTC))
    expires_at    = Column(DateTime, nullable=False)      # auto-delete after this
    signed_at     = Column(DateTime, nullable=True)
    downloaded_at = Column(DateTime, nullable=True)

    # Relationships
    template         = relationship("ContractTemplate")
    template_version = relationship("ContractTemplateVersion")
    creator          = relationship("User")
    audit_trail      = relationship("SigningAuditTrail", back_populates="submission", uselist=False)
```

### 1.2 New model: `SigningAuditTrail`

File: `app/models/signing_audit_trail.py`

Immutable record created at signing time. Never deleted.

```python
class SigningAuditTrail(Base):
    __tablename__ = "signing_audit_trails"

    id                  = Column(Integer, primary_key=True)
    submission_uuid     = Column(String, ForeignKey("submissions.uuid"), nullable=False)

    # Document integrity
    document_hash       = Column(String, nullable=False)  # SHA-256 of rendered HTML before signing

    # Signer evidence
    recipient_email     = Column(String, nullable=True)
    recipient_ip        = Column(String, nullable=False)
    user_agent          = Column(String, nullable=True)
    browser_language    = Column(String, nullable=True)
    timezone            = Column(String, nullable=True)
    screen_resolution   = Column(String, nullable=True)
    signer_full_name    = Column(String, nullable=False)  # entered by signer on signing screen

    # Consent evidence
    confirmed_read      = Column(Boolean, nullable=False)  # checkbox 1
    confirmed_esign     = Column(Boolean, nullable=False)  # checkbox 2

    # Timestamps
    code_verified_at    = Column(DateTime, nullable=False)
    contract_viewed_at  = Column(DateTime, nullable=True)
    signed_at           = Column(DateTime, nullable=False)

    # Owner evidence
    creator_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator_ip          = Column(String, nullable=True)

    submission = relationship("Submission", back_populates="audit_trail")
```

### 1.3 Update `SubmissionStatus` enum

File: `app/models/enums.py`

Add new statuses:
```python
class SubmissionStatus(str, enum.Enum):
    PENDING    = "pending"     # created, waiting for client to sign
    SIGNED     = "signed"      # client signed, owner has not yet downloaded
    COMPLETED  = "completed"   # owner downloaded — blob deleted
    DECLINED   = "declined"    # client declined
    EXPIRED    = "expired"     # TTL passed without signing
    CANCELLED  = "cancelled"   # owner cancelled
```

### 1.4 Update `FilledContract` model

File: `app/models/filled_contract.py`

- Remove `submitted_data` column
- Remove `rendered_content` column
- These fields will be dropped from the database in the migration

This model becomes legacy — existing rows remain readable but no new rows will store sensitive data. Eventually deprecate entirely once all submissions migrate to the new `Submission` model.

### 1.5 Alembic migration

Create: `migrations/versions/XXXX_add_secure_submission_models.py`

- Create `submissions` table
- Create `signing_audit_trails` table
- Drop `filled_contracts.submitted_data` column
- Drop `filled_contracts.rendered_content` column

---

## Phase 2 — Sensitive placeholder detection

File: `app/services/placeholder_service.py`

Add a set of known sensitive placeholders:

```python
SENSITIVE_PLACEHOLDERS = {
    "client_ID",
    "passport",
    "personal_code",
    "identity_number",
    "driver_license",
}
```

Add a method:

```python
@staticmethod
def has_sensitive_fields(content: str) -> bool:
    fields = PlaceholderService.extract_placeholders(content)
    return bool(set(fields) & SENSITIVE_PLACEHOLDERS)
```

This is called during submission creation to set `Submission.is_sensitive`.

---

## Phase 3 — Verification code service

File: `app/services/code_service.py`

New service, no database interaction, pure logic:

```python
class CodeService:
    MAX_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    @staticmethod
    def generate() -> tuple[str, str]:
        """Returns (plaintext_code, argon2_hash). Store only the hash."""
        code = f"{secrets.randbelow(1_000_000):06d}"
        hash_ = argon2.hash(code)
        return code, hash_

    @staticmethod
    def verify(plaintext: str, stored_hash: str) -> bool:
        try:
            return argon2.verify(stored_hash, plaintext)
        except VerifyMismatchError:
            return False

    @staticmethod
    def is_locked(submission: Submission) -> bool:
        ...

    @staticmethod
    def record_attempt(submission: Submission, db: Session) -> None:
        ...
```

Rate limiting: after 5 failed attempts lock for 15 minutes. Track `access_attempts` and `access_locked_until` on `Submission`.

---

## Phase 4 — Encryption service

File: `app/services/encryption_service.py`

```python
class EncryptionService:
    @staticmethod
    def generate_key() -> bytes:
        return os.urandom(32)  # AES-256

    @staticmethod
    def encrypt(data: bytes, key: bytes) -> tuple[bytes, bytes]:
        """Returns (ciphertext, nonce). Store both."""
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return ciphertext, nonce

    @staticmethod
    def decrypt(ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    @staticmethod
    def key_to_url_safe(key: bytes) -> str:
        return base64.urlsafe_b64encode(key).decode()

    @staticmethod
    def key_from_url_safe(s: str) -> bytes:
        return base64.urlsafe_b64decode(s.encode())
```

The AES key is **never written to the database**. It is embedded in the owner's download URL as a query parameter (`?k=...`). The owner's email is the only place it exists.

---

## Phase 5 — New signing router

File: `app/routers/signing.py`

All public identifiers are UUIDs. All sensitive endpoints have request body logging disabled.

### Endpoints

```
POST   /signing/submissions
       Body: { template_id, expires_in_hours, prefill, recipient_email? }
       Auth: owner JWT
       Action: create Submission, generate access code, optionally email client
       Returns: { uuid, access_code (if no email), expires_at }

GET    /signing/submissions/{uuid}
       Public (no auth)
       Action: verify submission exists, not expired, not completed
       Returns: { template_name, description, is_sensitive, status }

POST   /signing/submissions/{uuid}/verify-code
       Public
       Body: { code }
       Rate limit: 5/minute per IP
       Action: Argon2 verify access code, return signed session cookie
       Returns: { verified: true }

GET    /signing/submissions/{uuid}/preview
       Public + session cookie required
       Action: render template with owner prefill only (client fields shown as placeholders)
       Returns: { content: "<html>...", fields: [...], is_sensitive: bool }
       Logging: body NOT logged

POST   /signing/submissions/{uuid}/decline
       Public + session cookie required
       Action: mark DECLINED, notify owner
       Returns: { status: "declined" }

POST   /signing/submissions/{uuid}/sign
       Public + session cookie required
       Body: { payload, signature_image, signer_name, confirmed_read, confirmed_esign,
               browser_language, timezone, screen_resolution }
       Rate limit: 3/minute per IP
       Logging: body NOT logged, no payload fields in logs
       Action:
         1. Validate all fields present
         2. Render full contract HTML in RAM (never written to disk or DB)
         3. SHA-256 hash of rendered HTML → stored in audit trail
         4. Render PDF in RAM
         5. AES-256-GCM encrypt PDF with random key
         6. Store encrypted_pdf_blob + nonce in Submission
         7. Generate owner download code (6-digit, Argon2 hashed)
         8. Write SigningAuditTrail (no personal fields, no payload values)
         9. Update Submission.status = SIGNED
        10. Send owner notification email with download link + plaintext download code
        11. Stream PDF bytes directly to client as HTTP response (Content-Disposition: attachment)
       Returns: PDF file (binary stream)

GET    /signing/download/owner/{uuid}?k={aes_key_base64}
       Auth: owner JWT
       Query: k = base64url AES key
       Action:
         1. Verify owner JWT matches submission.creator_id
         2. Verify submission.status == SIGNED
         3. Decrypt PDF using k + stored nonce
         4. Stream PDF
         5. Wipe encrypted_pdf_blob and nonce from DB
         6. Wipe owner_download_code_hash from DB
         7. Set submission.status = COMPLETED
         8. Set submission.downloaded_at
       Returns: PDF file

DELETE /signing/submissions/{uuid}
       Auth: owner JWT
       Action: cancel pending submission
       Returns: { status: "cancelled" }
```

### What gets logged (logging middleware for signing endpoints)

Log ONLY:
- Timestamp
- Submission UUID
- HTTP status code
- Duration
- IP address

Never log:
- Request body
- Payload values
- Rendered HTML
- PDF bytes
- Verification codes
- Personal fields

---

## Phase 6 — Update link creation

File: `app/routers/links.py` and `app/services/link_service.py`

`POST /links` currently creates a `PublicLink` and returns a token. Update it to:

- Accept optional `recipient_email` field
- Call the new `SubmissionService.create_submission(...)` instead of just creating a link
- If `recipient_email` provided: send access email automatically, return `{ uuid, expires_at }`
- If not: return `{ uuid, access_code, expires_at }` (owner copies and sends manually)

The old `PublicLink` model can remain for existing data but no new links are created through the old flow.

---

## Phase 7 — Remove PDF attachment from email

File: `app/services/email_services.py`

- Delete `send_contract_signed_pdf` function entirely
- Delete the PDF attachment logic in `FilledContractService.confirm_submission`

Add new email functions:

```python
def send_signing_invitation(recipient_email, template_name, signing_url, access_code, expires_at):
    """Email sent to client: link + 6-digit code. No contract content."""

def send_owner_signed_notification(owner_email, template_name, download_url):
    """Email sent to owner after signing. Contains download link with embedded AES key."""
    # download_url = https://app.com/download/owner/{uuid}?k={base64_key}
    # No attachment. No PDF. No contract content.
```

---

## Phase 8 — Cleanup background job

File: `app/tasks/cleanup.py` (new file)

Scheduled task (run via cron or APScheduler):

```python
def cleanup_expired_submissions(db: Session):
    now = datetime.now(UTC)
    expired = db.query(Submission).filter(
        Submission.expires_at < now,
        Submission.status == SubmissionStatus.PENDING,
    ).all()
    for s in expired:
        s.status = SubmissionStatus.EXPIRED
        s.encrypted_pdf_blob = None
        s.encryption_nonce = None
        s.access_code_hash = None
        s.owner_download_code_hash = None
    db.commit()
```

Run every 15 minutes. Audit trail rows are never deleted.

---

## Phase 9 — Frontend changes

Working directory: `/Users/justasstulpinas/Pacta_front_end/pacta-frontend`

### 9.1 Updated link generation page

Path: `src/app/dashboard/templates/[id]`

Currently shows "Generate Link" with prefill fields. Update to:

- Add "Send to email" text input (optional)
- On submit:
  - If email provided: show confirmation ("Invitation sent to [email]")
  - If no email: show the link + 6-digit code in a copyable box
  - Show expiry time
- Remove the old "Copy link" only behavior

### 9.2 New signing page

Path: `src/app/sign/[uuid]` (new route, replaces existing signing flow)

**Step 1 — Code verification screen**
- Input: 6-digit code
- Submit → `POST /signing/submissions/{uuid}/verify-code`
- On success: show contract preview
- On failure: show "Invalid code. X attempts remaining."
- On lockout: show "Too many attempts. Try again in 15 minutes."

**Step 2 — Contract preview**
- Full rendered HTML (read-only)
- Scroll-to-bottom detection (user must scroll through entire document)
- Two buttons: "Decline" | "Proceed to Sign"
- If sensitive: show info banner "This contract requires your personal identification code"

**Step 3 — Fill data + sign**
- Form fields for all client placeholders (name, surname, address, ID etc.)
- **All fields stored in React state only — never in localStorage, sessionStorage, or cookies**
- Drawn signature pad (canvas)
- Two mandatory checkboxes:
  - "I confirm that I have read this contract."
  - "I agree to sign this document electronically."
- Full legal name text input (separate from form fields)
- Submit → `POST /signing/submissions/{uuid}/sign`
- On success: browser triggers PDF download automatically

**Step 4 — Success screen**
- "Contract signed. Your copy has been downloaded."
- No link to download again (one-time)

### 9.3 Owner download page

Path: `src/app/dashboard/submissions` (update existing) and `src/app/download/owner/[uuid]`

- Owner sees submission list with status badges (pending / signed / completed / declined)
- For `SIGNED` status: "Download Contract" button
- Clicking it opens `/download/owner/{uuid}?k={key}` — browser triggers PDF download
- After download: submission moves to `completed`, download button disappears

### 9.4 Remove old submission detail page behaviour

Path: `src/app/dashboard/submissions/[id]`

Currently shows `submitted_data` fields and allows confirming submission. Since `submitted_data` no longer exists:
- Remove the submitted data display table
- Remove "Confirm Submission" button (confirmation is now owner downloading the file)
- Show only: template name, status, signed at, audit trail summary

---

## Phase 10 — Security hardening

### Logging middleware

File: `app/middleware/secure_logging.py`

```python
BODY_SUPPRESSED_PATHS = {
    "/signing/submissions/{uuid}/sign",
    "/signing/submissions/{uuid}/verify-code",
}
```

Override request logging for these paths to emit only UUID, status, duration.

### Rate limiting (add to existing `app/limiter.py`)

- `POST /signing/submissions/{uuid}/verify-code` — 5/minute per IP
- `POST /signing/submissions/{uuid}/sign` — 3/minute per IP
- `GET /signing/download/owner/{uuid}` — 10/minute per user

### CSRF

FastAPI does not have built-in CSRF middleware. For state-changing endpoints called from the browser (sign, verify-code), enforce:
- `Content-Type: application/json` (browsers cannot send this cross-origin without CORS preflight)
- Ensure CORS `allow_origins` is strictly limited (already done in `main.py`)

### Session for signing flow

After code verification, issue a short-lived signed session cookie:
- `HttpOnly`, `Secure`, `SameSite=Strict`
- Payload: `{ submission_uuid, verified_at, exp: verified_at + 30min }`
- Sign with a separate secret from the JWT secret

---

## Phase 11 — Privacy policy and terms pages

Required before any real user data is collected. GDPR Article 13 obligation.

Frontend pages needed:
- `/privacy` — Privacy Policy (Lithuanian + English)
- `/terms` — Terms of Service (Lithuanian + English)

Must be linked from:
- Footer on all pages
- Signing page before consent checkboxes
- Registration page

Content must disclose:
- What data is collected (email, IP, audit trail)
- What is NOT stored (personal IDs, contract content)
- Data retention periods
- Right to erasure process

---

## Implementation order

```
[x] Phase 1  — Models + migration (submitted_data and rendered_content dropped)
[x] Phase 2  — Sensitive placeholder detection in PlaceholderService
[x] Phase 3  — CodeService (argon2-cffi)
[x] Phase 4  — EncryptionService (cryptography AES-256-GCM)
[x] Phase 5  — New signing router + SubmissionService
[x] Phase 6  — Update link creation schema (recipient_email field added)
[x] Phase 7  — Remove send_contract_signed_pdf, add new email functions
[x] Phase 8  — Cleanup background job for expired submissions
[x] Phase 10 — Rate limiting on new endpoints (via existing slowapi limiter)
[x] Phase 10 — Session cookie for post-verification state (HttpOnly, Secure, SameSite=Strict)
[x] Phase 10 — Logging middleware (suppress bodies on sensitive paths)
[ ] Phase 9  — Frontend: code verification screen
[ ] Phase 9  — Frontend: signing page (fill data + sign + auto-download)
[ ] Phase 9  — Frontend: owner download page
[ ] Phase 9  — Frontend: updated link generation (email option + code display)
[ ] Phase 11 — Privacy policy and terms pages
```

---

## Files to create (new)

| File | Purpose |
|------|---------|
| `app/models/submission.py` | New Submission model |
| `app/models/signing_audit_trail.py` | Immutable audit record |
| `app/services/code_service.py` | Argon2 code generation and verification |
| `app/services/encryption_service.py` | AES-256-GCM encrypt/decrypt |
| `app/services/submission_service.py` | Business logic for new signing flow |
| `app/routers/signing.py` | All new signing endpoints |
| `app/middleware/secure_logging.py` | Suppress body logging on sensitive paths |
| `app/tasks/cleanup.py` | Expired submission cleanup job |
| `migrations/versions/XXXX_secure_submissions.py` | Alembic migration |

## Files to modify (existing)

| File | Change |
|------|--------|
| `app/models/enums.py` | Add PENDING, SIGNED statuses |
| `app/models/filled_contract.py` | Remove submitted_data, rendered_content columns |
| `app/models/__init__.py` | Import new models |
| `app/services/placeholder_service.py` | Add SENSITIVE_PLACEHOLDERS set and has_sensitive_fields() |
| `app/services/email_services.py` | Remove send_contract_signed_pdf, add new email functions |
| `app/services/filled_contract_service.py` | Remove PDF attachment logic from confirm_submission |
| `app/routers/links.py` | Accept recipient_email, delegate to new SubmissionService |
| `app/main.py` | Include signing router, register cleanup task |
| `requirements.txt` | Add argon2-cffi, cryptography |

## Files to delete (after migration)

| File | Reason |
|------|--------|
| `app/services/contract_submission_service.py` | Replaced by new SubmissionService |

---

## What this does NOT implement

- Qualified Electronic Signature (QES) — requires Smart-ID or Mobile-ID integration
- Smart-ID / Mobile-ID — planned for future provider abstraction layer
- Long-term archival of signed contracts — owner is responsible for their download
- Multi-signer workflows — single signer only for now
