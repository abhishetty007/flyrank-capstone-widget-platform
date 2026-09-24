# FlyRank Capstone — Evidence

This document records the verification performed for the Embeddable Widget & Lead-Capture Platform.

---

## 1. Environment Verification

### PostgreSQL

PostgreSQL was run using Docker Compose.

Database connection was verified successfully with:

```text
current_user: flyrank
current_database: flyrank

The database is exposed locally through:

127.0.0.1:5433
Database migrations

Alembic migrations were initialized and applied successfully.

The database contains the application tables:

users
widgets
submissions
notification_jobs

The Alembic migration history is at the latest revision.

2. Authentication Evidence

The authentication API was manually tested.

Verified:

User registration
Successful login
Incorrect password rejection
JWT token generation
Protected endpoint access
Invalid/stale token rejection
Owner-authenticated widget APIs

JWT tokens are generated using the secret stored in .env.

Passwords are stored using bcrypt hashes rather than plaintext passwords.

3. Widget Management Evidence

Authenticated widget management was tested through the API.

Verified:

Widget creation
Widget listing
Individual widget retrieval
Widget update
Widget deletion
Public widget configuration retrieval

Widget updates increment the widget version.

Public widget configuration is available through:

GET /widgets/public/{public_id}
4. Cross-Origin Widget Evidence

The customer website runs separately from the FastAPI backend:

Customer site:
http://127.0.0.1:5500

Backend:
http://127.0.0.1:8000

The customer website successfully loads:

/widget/widget.js

The embedded widget successfully retrieves its public configuration and renders on the customer website.

This demonstrates the intended cross-origin widget flow.

5. Successful Lead Submission

A normal visitor submission was successfully performed through the embedded widget.

Observed flow:

Customer Website
      ↓
Embedded Widget
      ↓
POST /public/submissions
      ↓
Validation
      ↓
Rate Limit
      ↓
Honeypot
      ↓
Idempotency
      ↓
Geo Enrichment
      ↓
PostgreSQL
      ↓
Notification Job

The customer-facing widget displayed:

Thank you! Your submission was received.

The API returned HTTP:

201 Created

The submission was visible in the owner dashboard.

6. Dashboard Evidence

The customer dashboard was tested successfully.

Dashboard:

http://127.0.0.1:5500/dashboard.html

The dashboard uses the owner's JWT token and retrieves:

GET /dashboard/submissions

Verified dashboard information includes:

Submission ID
Widget ID
Name
Email
IP address
Country
City
Geo provider
Created timestamp

Dashboard queries are restricted to widgets owned by the authenticated user.

7. Request Size Protection

The public submission endpoint includes a 10 KB request-size limit.

Oversized requests are rejected with:

413 Submission payload is too large.

Malformed request input is handled through FastAPI/Pydantic validation rather than being allowed to reach database persistence.

8. Rate Limiting Evidence

The public submission endpoint uses an IP + widget rate-limit key.

Configuration:

Maximum requests: 5
Window: 60 seconds

Burst testing produced:

HTTP 429 Too Many Requests

Normal submissions continue to work outside the rate-limit condition.

9. Honeypot Protection

The embedded widget contains a hidden honeypot field.

The field is not included in the normal submission payload.

If the honeypot is populated, the backend returns an accepted response without storing the submission.

This provides a lightweight automated spam trap.

10. Idempotency Evidence

Submissions support an optional idempotency key.

The database contains a unique constraint on:

(widget_id, idempotency_key)

The API also performs an application-level duplicate check.

Concurrent duplicate insertion is handled using an IntegrityError recovery path.

A repeated idempotency key returns the existing submission rather than creating another submission.

11. Geo Fallback Automated Tests

Automated tests were created in:

backend/tests/test_geo.py

The test suite verifies:

Provider A success
Provider A → success
Provider B → not called

Result:

PASSED
Provider A failure
Provider A → failure
Provider B → success

Result:

PASSED
Both providers fail
Provider A → failure
Provider B → failure

Result:

None

The submission flow can therefore continue without geographic information.

Result:

PASSED
Private IP

Private IP addresses do not trigger external geo providers.

Result:

PASSED

Final geo test result:

4 passed
12. Background Notification Job Evidence

Automated testing was created in:

backend/tests/test_notifications.py

The notification service supports up to:

3 attempts

The automated failure test deliberately makes the notification service fail.

Observed behavior:

Attempt 1 → failure
Attempt 2 → failure
Attempt 3 → failure
Job → failed
Failure alert → generated

Test result:

1 passed

This verifies the retry and failure-handling path.

13. Widget Cache and Version Evidence

The widget bundle is served through:

GET /widget/widget.js

The endpoint was tested using curl.

Observed response:

HTTP/1.1 200 OK
cache-control: public, max-age=300, must-revalidate
x-widget-version: 1

This verifies:

Successful widget bundle delivery
Cache-Control policy
Explicit widget bundle version
14. CORS Evidence

The backend allows the local customer-site origins:

http://127.0.0.1:5500
http://localhost:5500

The customer website successfully loads and communicates with the backend from a different origin.

The backend does not use:

Access-Control-Allow-Origin: *
15. Automated Test Summary

The project currently contains automated tests for:

Geo provider A success
Geo provider fallback
Both geo providers unavailable
Private IP handling
Notification retry/failure handling

Full test suite result:

5 passed

The tests were executed using:

$env:PYTHONPATH="."
pytest -v
16. Security / Configuration Evidence

Sensitive configuration is loaded through environment variables.

.env contains local development secrets and is excluded from Git.

The repository contains:

.env.example

rather than the actual development secret.

The database URL and JWT secret are therefore not hardcoded in the application source.

17. Manual Acceptance Flow

The following end-to-end flow was manually verified:

1. Start PostgreSQL with Docker
        ↓
2. Start FastAPI
        ↓
3. Start customer website
        ↓
4. Open customer site
        ↓
5. Embedded widget loads
        ↓
6. Visitor submits lead
        ↓
7. API returns 201
        ↓
8. Submission is persisted
        ↓
9. Notification job is created
        ↓
10. Dashboard displays submission
18. Known Development Scope

The current implementation uses console output as the notification side effect.

The geo providers are external services and local private IP addresses do not produce public geographic information.

The widget UI is intentionally minimal, consistent with the capstone's realistic-scope guidance.

The application is currently designed for local development and evaluation rather than production deployment.

19. Evidence Status
Requirement	Status
Authentication	Verified
JWT protection	Verified
Widget CRUD	Verified
Tenant isolation	Implemented
Embeddable widget	Verified
Cross-origin communication	Verified
Public submissions	Verified
Request-size protection	Implemented
Rate limiting	Verified
Honeypot	Implemented
Idempotency	Implemented
Geo fallback	4 automated tests passed
Background job	Verified
Retry handling	1 automated test passed
Failure alert	Verified
PostgreSQL persistence	Verified
Alembic migrations	Verified
Widget caching	Verified
Widget version header	Verified
Customer dashboard	Verified
Environment secrets	Implemented
Automated test suite	5 passed