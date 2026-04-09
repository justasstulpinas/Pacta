1. OVERVIEW

Backend API for contract template creation with open link signing, backend can generate HTML, DOCX, PDF files from signed contracts, user must be legged in to send a request.

Core characteristics:

SQLAlchemy ORM with SQLite default storage (`pacta.db`).
JWT-based authentication with role/permission checks.
Template versioning and immutable submission snapshots.

2. RUNTIME 

Application entrypoint:

`app/main.py`

Startup behavior:

Imports all ORM models via `import app.models`.
Creates database tables with `Base.metadata.create_all(bind=engine)`.
Applies lightweight SQLite compatibility alterations in `_ensure_schema_compatibility()`.
Seeds RBAC defaults via `seed_rbac(...)`.
Registers routers and exception handlers.
Mounts static uploads at `/uploads`.

3. ARCHITECTURE

API Layer (`app/routers`)

HTTP routing and request/response mapping:

`auth.py`: register, login/token, logout, current user
`templates.py`: CRUD template lifecycle and submission list.
`links.py`: public link creation, public template view, public submit.
`contracts.py`: submission read/confirm and document download in PDF or DOCX format.
`contacts.py`: user contact list/create/update.
`profile.py`: profile read/update/delete and picture upload/delete.

Dependencies (`app/dependencies`)

Request-scoped dependencies:

`auth.py`: token decoding, revocation check, current user confirmation
`authorization.py`: User action and permission guard for specific user type

Services (`app/services`)

Business logic:

`AuthService`: registration, credential verification, token issue/revoke.
`TemplateService`: template lifecycle and template version creation.
`LinkService`: public link generation, placeholder validation, submission creation.
`ContractService`: submission listing for a template.
`FilledContractService`: submission read/confirm states.
`ContractSubmissionService`: document rendering pipeline.
`ProfileService` and `ContactService`: profile/contact business logic.
`PolicyService`: centralized role/permission checks.
`PlaceholderService`: placeholder extraction, classification.

Repositories (`app/repositories`)

Database access:

`TemplateRepository`: templates, versions, links, submissions.
`UserRepository`, `UserProfileRepository`, `ContactRepository`, `RevokedTokenRepository`.

Data Layer (`app/models`, `app/schemas`)

`models/`: table definitions.
`schemas/`: Helper files for input standartization.

Rendering Layer (`app/renderers`)

`document_renderer.py`: HTML file renderer
`pdf_renderer.py`: HTML to PDF (WeasyPrint).
`docx_renderer.py`: HTML to DOCX (python-docx and BeautifulSoup).

4. Domain Model

Primary entities:

`User`: account with `roles`, `contract_templates`, `contacts`, one profile per user `profile`.
`Role`, `Permission`, `user_roles`, `role_permissions`: RBAC model.
`ContractTemplate`: owner-bound template with lifecycle status and soft-delete.
`ContractTemplateVersion`: content versions for each template.
`PublicLink`: tokenized link with expiry, that might have preentered info.
`FilledContract`: submitted contract with payload that has rendered output and status history.
`Contact`: owner contact entries from competed contracts
`UserProfile`: single profile row per user.
`RevokedToken`: invalidated JWT IDs (`jti`) for logout or ended sessions.

Important enums:

keeps plain strings outs of databases to minimize input error.

`TemplateStatus`: `draft`, `active`, `archived`.
`SubmissionStatus`: `submitted`, `confirmed`, `completed`, `cancelled`.

5. Business Flows

5.1 Authentication and Session

1. `/auth/register` creates user and assigns `creator` role when available.
2. `/auth/login` or `/auth/token` validates password and provides JWT.
3. Protected routes use `get_current_user(...)`:
   decode JWT,
   reject revoked token (`revoked_tokens`),
   load user from DB.
4. `/auth/logout` stores JWT `jti` in revocation list.

5.2 Template Lifecycle and Versioning

1. Template is created as `draft`.
2. Version `1` is created immediately in `contract_template_versions`.
3. Editing content creates next version number only when content changed.
4. State transitions:
   `draft -> active`
   `active -> archived`
5. Soft delete is blocked for `active` templates template can only be deleted as `draft` or `archived`.

5.3. Public Link and Submission

1. Only `active` templates can generate links.
2. Latest template version is used at link creation.
3. Placeholder handling:
   `owner_*` must be prefilled by owner, link cannot be generated until these are prefilled.
   `sys_*` is resolved by system (used for date).
   remaining fields are for user to fill.
4. Public submit validates payload fields exactly.
5. Submission stores:
   template version number and version id,
   original submitted payload,
   rendered content snapshot,
   request metadata (IP, user-agent),
   deterministic submission hash.

5.4 Submission Confirmation and Export

1. Owner/admin retrieves submission.
2. Confirm operation allowed only from `submitted`.
3. Export pipeline:
   submission `rendered_content` to HTML wrapper,
   HTML to PDF or DOCX,
   file returned as attachment.

6. Authorization Model

Authorization is policy-centric (`PolicyService`):

Owner access is default rule.
Admin override is permission-based (`admin:all`).
Permission checks operate on role-attached boundaries.
Services enforce authorization before changing or returning protected endpoints or data.

7. Error Handling

Domain exceptions (`app/core/exceptions.py`) are mapped in `app/main.py` to have uniform HTTP responses:

`InvalidCredentialsError` -> 401
`PermissionDeniedError` / `ForbiddenError` -> 403
`UnauthorizedError` -> 401
`NotFoundError` -> 404
`ValidationError` -> 400

8. Data and Infra Notes

Default database: SQLite at `sqlite:///./pacta.db`
No migration framework is integrated.
File uploads are stored under `app/uploads`.

9. Final notes:

API is being tested with Next.js front end to be fully operational, e-signature api or model needs to be
implimented to be fully operational.