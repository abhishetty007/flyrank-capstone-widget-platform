# Embeddable Widget & Lead-Capture Platform
## Phase 1 — Design Document

## 1. Problem

Build a backend platform that allows customers to create embeddable
widgets such as signup forms, contact forms, and call-to-action widgets.

A customer receives a single JavaScript `<script>` snippet that can be
placed on another website.

When a visitor submits the widget:

1. The browser sends the submission to our public API.
2. The API validates the request.
3. Abuse protection is applied.
4. The visitor IP is enriched with geolocation.
5. The submission is stored.
6. A non-critical notification side effect is triggered.
7. The widget owner can view submissions and basic analytics.

The backend must treat the public internet as untrusted input.

---

## 2. Actors

### Widget Owner

An authenticated customer who can:

- Register an account
- Log in
- Create widgets
- View their widgets
- Update their widgets
- Delete their widgets
- Generate an embed snippet
- View submissions
- View basic analytics

### Website Visitor

An unauthenticated visitor who:

- Loads an embedded widget
- Fills in the form
- Submits the form

Visitors must never have access to private owner APIs.

---

## 3. Multi-Tenant Model

Each registered customer represents a tenant.

Every widget belongs to exactly one tenant.

Every submission belongs to exactly one widget and tenant.

Tenant isolation must be enforced by the backend.

Example:

    Tenant A
       |
       +-- Widget A1
       +-- Widget A2
             |
             +-- Submissions

    Tenant B
       |
       +-- Widget B1
             |
             +-- Submissions

Tenant A must never be able to:

- Read Tenant B's widgets
- Modify Tenant B's widgets
- Delete Tenant B's widgets
- Read Tenant B's submissions
- Read Tenant B's analytics

Tenant ownership must be included in database queries and authorization
checks rather than relying on frontend filtering.

---

## 4. Widget Model

A widget contains:

- id
- tenant_id
- public_id
- type
- title
- description
- form fields
- button text
- display options
- version
- created_at
- updated_at

### Widget Types

The initial implementation supports:

- signup
- contact
- cta

The system may support popover later.

### Form Field Model

Each field contains:

- name
- label
- type
- required
- validation rules

Example:

    {
      "name": "email",
      "label": "Email",
      "type": "email",
      "required": true
    }

---

## 5. Submission Model

A submission contains:

- id
- widget_id
- tenant_id
- idempotency_key
- submitted form data
- IP address
- country
- city
- geo provider
- created_at

The visitor's submitted form data is stored as structured JSON where
appropriate.

The backend validates the submission before it reaches business logic.

The backend never trusts client-side validation.

---

## 6. Database Model

Initial PostgreSQL tables:

### users

- id
- email
- password_hash
- created_at
- updated_at

### sessions

- id
- user_id
- token_hash
- expires_at
- revoked_at
- created_at

### widgets

- id
- tenant_id
- public_id
- type
- title
- description
- fields
- button_text
- display_options
- version
- created_at
- updated_at

### submissions

- id
- widget_id
- tenant_id
- idempotency_key
- payload
- ip_address
- country
- city
- geo_provider
- created_at

### notification_jobs

- id
- submission_id
- status
- attempts
- last_error
- created_at
- updated_at

Indexes will be added for:

- users.email
- widgets.tenant_id
- widgets.public_id
- submissions.widget_id
- submissions.tenant_id
- submissions.created_at
- submissions.idempotency_key

---

## 7. Architecture

The application follows a layered architecture:

    HTTP Layer
        |
        v
    Middleware
        |
        +-- Authentication
        +-- Authorization
        +-- CORS
        +-- Rate Limiting
        +-- Request ID
        |
        v
    Service / Business Logic
        |
        +-- Widget Service
        +-- Submission Service
        +-- Geo Service
        +-- Notification Service
        |
        v
    Repository / Data Access
        |
        v
    PostgreSQL

External services:

    Submission Service
          |
          +----> Geo Provider A
          |
          +----> Geo Provider B
          |
          +----> Background Notification Worker

The application will use background processing for non-critical work
such as notification delivery.

---

## 8. Three Request Paths

The system has three separate request paths.

### Path A — Widget Owner

    Owner
      |
      v
    Authenticated API
      |
      v
    Authentication
      |
      v
    Authorization
      |
      v
    Widget Service
      |
      v
    PostgreSQL

Used for widget management and dashboard operations.

---

### Path B — Customer Website

    Customer Website
          |
          v
    widget.js
          |
          v
    Public Widget Config API
          |
          v
    Render Widget

Widget configuration is public but contains only the information
required to render the widget.

The configuration endpoint uses HTTP caching.

---

### Path C — Website Visitor

    Visitor
       |
       v
    POST Submission
       |
       v
    CORS
       |
       v
    Request Validation
       |
       v
    Rate Limiting
       |
       v
    Spam Protection
       |
       v
    Geo Enrichment
       |
       +---- Provider A
       |       |
       |       +-- success
       |
       +---- failure
               |
               v
           Provider B
               |
               +-- failure
                       |
                       v
                   Continue without geo
       |
       v
    PostgreSQL
       |
       v
    Background Notification Job

A failure in geo enrichment or notification must not destroy a valid
submission.

---

## 9. Authentication API

### POST /api/auth/register

Creates a customer account.

### POST /api/auth/login

Authenticates the customer.

### POST /api/auth/logout

Ends the authenticated session.

### GET /api/auth/me

Returns the current authenticated user.

Authentication is required for owner/admin endpoints.

Passwords are stored using a secure password hashing algorithm.

---

## 10. Widget API

### POST /api/widgets

Create a widget.

Authentication required.

### GET /api/widgets

List widgets belonging to the authenticated tenant.

### GET /api/widgets/{id}

Get one widget belonging to the authenticated tenant.

### PATCH /api/widgets/{id}

Update a widget belonging to the authenticated tenant.

### DELETE /api/widgets/{id}

Delete a widget belonging to the authenticated tenant.

All widget operations enforce tenant ownership.

---

## 11. Embed API

After creating a widget, the backend returns a snippet similar to:

    <script
      src="http://localhost:8000/widget.js?id=abc123">
    </script>

The public widget ID is opaque and is not the internal database ID.

---

## 12. Public Widget Configuration

### GET /widgets/{public_id}/config

Public endpoint.

Returns only the configuration needed by the widget.

The response is cached using an appropriate `Cache-Control` header.

Example:

    Cache-Control: public, max-age=60

No private tenant information is returned.

---

## 13. Widget JavaScript

### GET /widget.js

Serves the widget JavaScript.

The widget:

1. Reads its public widget ID.
2. Requests widget configuration.
3. Renders the form.
4. Validates basic user input.
5. Sends the submission to the public API.
6. Displays success or error feedback.

The server remains responsible for final validation.

The JavaScript bundle will be versioned or cache-busted when changed.

---

## 14. Public Submission API

### POST /widgets/{public_id}/submissions

Accepts visitor submissions.

The endpoint must:

1. Validate Content-Type.
2. Enforce a request body size limit.
3. Parse JSON safely.
4. Validate required fields.
5. Validate field types and lengths.
6. Apply CORS rules.
7. Apply rate limiting.
8. Apply spam protection.
9. Perform geo enrichment.
10. Store the submission.
11. Enqueue a non-critical notification.
12. Return success.

Malformed or oversized requests must return clean 4xx responses.

They must never produce an unexpected 500 response.

---

## 15. CORS

The customer test website will run on a different origin from the API.

Example:

    API:
    http://localhost:8000

    Customer website:
    http://localhost:5500

The public submission endpoint must support:

- Cross-origin POST requests
- OPTIONS preflight requests
- Correct CORS response headers

Private authenticated APIs must not use unrestricted wildcard CORS.

---

## 16. Rate Limiting

The public submission endpoint will use configurable rate limits.

Rate limiting will consider:

- IP address
- Widget

When the limit is exceeded:

    HTTP 429 Too Many Requests

The API should provide appropriate rate-limit information such as
`Retry-After` when useful.

The implementation should be capable of using Redis so the limit can
work consistently across multiple application instances.

---

## 17. Spam Protection

The initial spam control is a honeypot field.

Example:

    website_url

The field is hidden from normal visitors.

If a bot fills the field:

- The submission is rejected or silently dropped.
- Geo enrichment is not required.
- Notification side effects must not run.
- It must not be stored as a legitimate lead.

This behavior will have an automated test.

---

## 18. Geo Enrichment

The submission IP is enriched using a fallback chain:

    Provider A
        |
        +-- success --> use result
        |
        +-- failure
                |
                v
            Provider B
                |
                +-- success --> use result
                |
                +-- failure --> store without geo

The capstone specifies:

Provider A:
- ip-api.com

Provider B:
- ipapi.co

External calls must have timeouts.

Geo provider failure must never cause a valid submission to fail.

The provider used will be recorded when enrichment succeeds.

Tests will use deterministic mocked providers to prove the fallback.

---

## 19. Idempotency

The submission endpoint accepts:

    Idempotency-Key: <unique-key>

Repeated requests using the same key for the same widget must not
create duplicate submissions.

The database will enforce the uniqueness rule where appropriate.

Example:

    Request 1
    Idempotency-Key: abc123
         |
         +--> create submission

    Request 2
    Idempotency-Key: abc123
         |
         +--> return existing result
              no duplicate row

---

## 20. Safe Side Effects

After a submission is stored, a notification is queued.

Possible implementation:

- Local console notification
- Mailpit

The notification is NOT part of the critical submission path.

Correct flow:

    Store submission
          |
          v
    Return success
          |
          v
    Background notification

If notification fails:

- The submission remains stored.
- The job can retry.
- The failure is logged.
- The visitor still receives a successful submission response.

---

## 21. Background Job

At least one real background job will be implemented.

Initial job:

    Send submission notification

The worker will support:

- queued jobs
- retries
- attempt count
- failure state
- error recording
- structured logging

Slow/non-critical work must not block the main submission request.

---

## 22. Dashboard API

Authenticated owner endpoints:

### GET /api/dashboard/submissions

Returns paginated submissions belonging to the authenticated tenant.

### GET /api/dashboard/stats

Returns basic analytics:

- total submissions
- submissions over time
- submissions by widget
- country breakdown
- city breakdown

### GET /api/dashboard/widgets/{id}/stats

Returns statistics for one tenant-owned widget.

All queries enforce tenant isolation.

---

## 23. Customer Test Website

Create a plain HTML website served from a different origin.

Example:

    http://localhost:5500

It will load the widget using:

    <script
      src="http://localhost:8000/widget.js?id=abc123">
    </script>

This proves that the widget works outside the API's origin.

No real domain, CDN, or hosting is required.

---

## 24. Security Boundaries

The backend is the security boundary.

Never trust:

- frontend validation
- URL IDs
- JSON payloads
- client-provided tenant IDs
- widget configuration from the browser
- IP-derived data
- request headers
- public widget IDs

Security controls include:

- password hashing
- authentication
- authorization
- tenant isolation
- input validation
- request-size limits
- rate limiting
- spam protection
- CORS restrictions
- parameterized SQL
- environment-based secrets
- external request timeouts
- safe error responses
- request IDs
- structured logging

Secrets must never appear in source code or logs.

---

## 25. Non-Goal

The initial version will NOT attempt to become a complete
form-builder SaaS.

Specifically, it will not include:

- drag-and-drop form design
- advanced visual customization
- real production CDN infrastructure
- real cloud deployment
- complex marketing automation
- advanced CRM integrations

The goal is to prove the backend engineering patterns required by the
capstone.

---

## 26. Phase 1 Gate

Phase 1 is complete when this design document is committed to the
repository and the following are clearly defined:

- Problem
- Actors
- Widget model
- Submission model
- Tenant isolation
- Database model
- API surface
- Layered architecture
- Three request paths
- Embed flow
- Security boundaries
- Explicit non-goal

Next phase:

Build the hardened submission path:
validation + CORS + rate limiting + spam protection +
geo fallback + safe side effects.