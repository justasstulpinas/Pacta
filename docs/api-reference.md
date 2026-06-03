# Pacta API Reference

## Base URL
```
http://localhost:8000
```

Interactive docs: `http://localhost:8000/docs`

---

## Auth & JWT

| Detail | Value |
|---|---|
| Token lifetime | 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`) |
| Client storage | `localStorage` or httpOnly cookie |
| How to send | `Authorization: Bearer <token>` header |
| Token refresh | Not implemented — re-login when expired |

---

## Auth Endpoints

### Register
```
POST /auth/register
Auth: No
Body:  { "email": "string", "password": "string" }
Response: { "id": int, "email": "string" }
```

### Login
```
POST /auth/login
Auth: No
Body: { "email": "string", "password": "string" }
Response: { "access_token": "string", "token_type": "bearer" }
```

### Login (OAuth2 form — used by Swagger)
```
POST /auth/token
Auth: No
Body: form-data { username, password }
Response: { "access_token": "string", "token_type": "bearer" }
```

### Current user
```
GET /auth/me
Auth: Yes
Response: { "id": int, "email": "string" }
```

### Logout
```
POST /auth/logout
Auth: Yes
Response: { "status": "logged_out" }
```

---

## Templates

### List templates
```
GET /templates
Auth: Yes
Response: [{ "id", "name", "description", "content", "status" }]
```

### Get template
```
GET /templates/{template_id}
Auth: Yes
Response: { "id", "name", "description", "content", "status" }
```

### Create template
```
POST /templates
Auth: Yes
Body: { "name": "string", "description": "string|null", "content": "string" }
Response: { "id", "name", "description", "content", "status" }
```

### Update template
```
PUT /templates/{template_id}
Auth: Yes
Body: { "name"?, "description"?, "content"? }
Response: { "id", "name", "description", "content", "status" }
```

### Activate template
```
PATCH /templates/{template_id}/activate
Auth: Yes
Response: { "id", "name", "description", "content", "status" }
```

### Archive template
```
PATCH /templates/{template_id}/archive
Auth: Yes
Response: { "id", "name", "description", "content", "status" }
```

### Soft delete template
```
DELETE /templates/{template_id}
Auth: Yes
Response: { "id", "name", "description", "content", "status" }
```

### List submissions for template
```
GET /templates/{template_id}/submissions?limit=20&offset=0&status=string
Auth: Yes
Response: [FilledContractResponse]
```

---

## Public Links

### Create link
```
POST /links
Auth: Yes
Body: { "template_id": int, "expires_in_hours": int, "prefill": {} }
Response: { "id", "token", "expires_at" }
```

### Revoke link
```
DELETE /links/{link_id}
Auth: Yes
Response: { "id", "token", "expires_at" }
```

### Get public template (no auth)
```
GET /links/public/{token}
Auth: No
Response: { "name", "description", "content", "fields": ["string"] }
```

### Submit contract (no auth)
```
POST /links/public/{token}/submit
Auth: No
Rate limit: 5/minute per IP
Body: {
  "payload": { "field_name": "value" },
  "signature_image": "base64string|null",
  "submitter_email": "string"
}
Response: { "status": "submitted", "id": int }
```

---

## Contracts / Submissions

### Get submission
```
GET /contracts/submissions/{submission_id}
Auth: Yes
Response: FilledContractResponse
```

### Confirm submission
```
POST /contracts/submissions/{submission_id}/confirm
Auth: Yes
Response: FilledContractResponse
```

### Get submission HTML
```
GET /contracts/submissions/{submission_id}/document
Auth: Yes
Response: { "html": "string" }
```

### Download PDF
```
GET /contracts/submissions/{submission_id}/pdf
Auth: Yes
Response: binary PDF file (Content-Disposition: attachment)
```

### Download DOCX
```
GET /contracts/submissions/{submission_id}/docx
Auth: Yes
Response: binary DOCX file (Content-Disposition: attachment)
```

---

## Profile

### Get profile
```
GET /profile
Auth: Yes
Response: {
  "user_id": int,
  "email": "string",
  "profile_name": "string|null",
  "company_name": "string|null",
  "address": "string|null",
  "phone_number": "string|null",
  "avatar_url": "string|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Update profile
```
PUT /profile
Auth: Yes
Body: { "profile_name"?, "company_name"?, "address"?, "phone_number"? }
Response: ProfileOut
```

### Delete account
```
DELETE /profile
Auth: Yes
Response: 204 No Content
```

### Upload avatar
```
POST /profile/avatar
Auth: Yes
Body: multipart/form-data { file: image/jpeg|png|webp, max 5MB }
Response: { "avatar_url": "string" }
```

### Delete avatar
```
DELETE /profile/avatar
Auth: Yes
Response: { "avatar_url": null }
```

---

## Contacts

### List contacts
```
GET /contacts
Auth: Yes
Response: [{ "id", "name", "email", "phone", "address" }]
```

### Create contact
```
POST /contacts
Auth: Yes
Body: { "name"?, "email"?, "phone"?, "address"? }
Response: ContactOut
```

### Update contact
```
PATCH /contacts/{contact_id}
Auth: Yes
Body: { "name"?, "email"?, "phone"?, "address"? }
Response: ContactOut
```

---

## FilledContractResponse Shape

```json
{
  "id": 1,
  "template_id": 1,
  "template_version": 1,
  "link_id": 1,
  "submitted_data": { "field_name": "value" },
  "rendered_content": "string",
  "status": "submitted|confirmed|completed|cancelled",
  "submitted_at": "2026-01-01T00:00:00",
  "confirmed_at": "2026-01-01T00:00:00|null",
  "ip_address": "string",
  "user_agent": "string|null",
  "signature_image": "base64string|null",
  "submission_hash": "string",
  "submitter_email": "string|null"
}
```

---

## Error Format

```json
{ "detail": "string" }
```

Validation errors:
```json
{
  "detail": [
    { "type": "string", "loc": ["body", "field"], "msg": "string", "input": {} }
  ]
}
```

| Status | Meaning |
|---|---|
| 400 | Bad request / validation error |
| 401 | Invalid or expired token |
| 403 | Forbidden — not your resource |
| 404 | Not found |
| 422 | Pydantic validation failed (missing/wrong fields) |
| 429 | Rate limit exceeded |
| 500 | Unhandled server error |

---

## CORS

Allowed origins (set via `FRONT_END_URL` in `.env`):
- `http://localhost:3000`
- `http://127.0.0.1:3000`

Update `FRONT_END_URL` in production `.env` to your Vercel domain.

---

## Template Status Values
```
draft → active → archived
```
- Only `draft` templates can be activated
- Only `active` templates can be archived
- Only `active` templates can generate public links
- Only `draft` or `archived` templates can be deleted

## Submission Status Values
```
submitted → confirmed → completed
                     → cancelled
```
- Only `submitted` submissions can be confirmed
