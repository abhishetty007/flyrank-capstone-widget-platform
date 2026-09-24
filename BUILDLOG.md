# FlyRank Capstone — Build Log

## Project

**Embeddable Widget & Lead-Capture Platform**

Technology:

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JavaScript
- Docker

---

# Phase 1 — Project Setup and Design

## Repository Setup

Created the dedicated project repository:

```text
flyrank-capstone-widget-platform
Initialized Git and created the initial repository structure.

Initial commit:

chore: initialize capstone repository
System Design

Created:

docs/design.md

The design defines:

Widget Owner
Website Visitor
Multi-tenant data model
Authentication flow
Widget management API
Public submission path
Rate limiting
Honeypot protection
Geo enrichment
Idempotency
Background notification jobs
Dashboard
Customer test site

The design was created before implementing the main backend functionality.

Phase 2 — Backend Foundation
FastAPI

Created the FastAPI application and API routing structure.

Main API groups:

/auth
/widgets
/public
/dashboard

Added:

GET /health
GET /
GET /protected
PostgreSQL

PostgreSQL was configured through Docker Compose.

The Docker database uses:

Database: flyrank
User: flyrank
Host: 127.0.0.1
Port: 5433

The host port is 5433 because a native PostgreSQL installation was already using port 5432.

Database connectivity was verified from Python and PostgreSQL CLI.

SQLAlchemy

Created SQLAlchemy models for:

User
Widget
Submission
NotificationJob

The submission model includes an idempotency constraint:

(widget_id, idempotency_key)
Alembic

Initialized Alembic and created migrations for the database schema.

Verified that migrations apply successfully using:

alembic upgrade head
Phase 3 — Authentication

Implemented:

User registration
User login
Password hashing
Password verification
JWT access tokens
Protected API routes

Passwords are hashed using bcrypt.

JWT configuration uses an environment-based secret.

The secret is loaded from:

.env

rather than being hardcoded in application source code.

Phase 4 — Widget Management

Implemented authenticated widget CRUD:

POST   /widgets/
GET    /widgets/
GET    /widgets/{widget_id}
PUT    /widgets/{widget_id}
DELETE /widgets/{widget_id}

Added public widget configuration:

GET /widgets/public/{public_id}

Widget owners are isolated by owner_id.

Widget updates increment the widget version.

Phase 5 — Embeddable Widget

Created:

widget/widget.js

The script:

Reads the widget's public ID.
Requests public widget configuration.
Dynamically renders the form.
Creates a hidden honeypot field.
Collects visitor input.
Generates an idempotency key.
Sends the submission to the backend.
Displays success or failure feedback.

The widget was tested on a separate customer website origin.

Customer site:

http://127.0.0.1:5500

Backend:

http://127.0.0.1:8000
Phase 6 — Public Submission Path

Implemented:

POST /public/submissions

The request path includes:

Request-size validation
        ↓
Widget lookup
        ↓
Rate limiting
        ↓
Honeypot
        ↓
Idempotency
        ↓
Geo enrichment
        ↓
Database persistence
        ↓
Notification job

The endpoint returns appropriate HTTP errors instead of allowing malformed conditions to become server errors.

Phase 7 — Rate Limiting

Implemented an in-memory IP + widget rate limiter.

Current development configuration:

Maximum requests: 5
Window: 60 seconds

Burst testing produced:

HTTP 429 Too Many Requests
Phase 8 — Honeypot Protection

Added a hidden honeypot field to the embedded widget.

Normal visitors do not interact with it.

If the honeypot is populated, the backend accepts the request response without persisting it as a normal lead.

Phase 9 — Idempotency

Implemented optional idempotency keys.

The database contains a unique constraint on:

widget_id + idempotency_key

The application also checks for existing submissions before insertion.

An IntegrityError recovery path handles concurrent duplicate requests.

Phase 10 — Geo Enrichment

Implemented two geographic providers:

Provider A: ip-api.com
Provider B: ipapi.co

Fallback behavior:

Provider A
    ↓ failure
Provider B
    ↓ failure
Continue without geo data

Private IP addresses are ignored because local development requests normally use addresses such as:

127.0.0.1
Phase 11 — Geo Testing

Created:

backend/tests/test_geo.py

Tests cover:

Provider A success
Provider A failure with Provider B fallback
Both providers failing
Private IP handling

Test result:

4 passed
Phase 12 — Background Notification Jobs

Created:

backend/app/services/notifications.py

The submission flow creates a notification job after persistence.

The development implementation prints the notification to the backend console.

The job supports:

Maximum attempts: 3

If the notification fails, the job records the error and retries.

After all attempts fail, the job is marked:

failed

and an application-level failure alert is printed.

Phase 13 — Notification Testing

Created:

backend/tests/test_notifications.py

The test deliberately makes the notification operation fail.

Verified:

Attempt 1 → failure
Attempt 2 → failure
Attempt 3 → failure
Job → failed
Alert → generated

Test result:

1 passed
Phase 14 — Dashboard

Created:

customer-site/dashboard.html

The dashboard allows an authenticated owner to view collected submissions.

It stores the JWT token in browser local storage during the development workflow.

The dashboard displays:

Submission ID
Widget ID
Name
Email
Country
City
Geo provider
Created timestamp
Phase 15 — CORS

Configured CORS for the local customer website origins:

http://127.0.0.1:5500
http://localhost:5500

The API does not use a wildcard origin.

Cross-origin widget loading and submission were tested successfully.

Phase 16 — Widget Caching and Versioning

Changed widget delivery from a generic static mount to an explicit route.

The widget endpoint:

GET /widget/widget.js

returns:

Cache-Control: public, max-age=300, must-revalidate
X-Widget-Version: 1

The endpoint was verified using curl.

Observed:

HTTP/1.1 200 OK
cache-control: public, max-age=300, must-revalidate
x-widget-version: 1
Phase 17 — Environment Security

Moved configuration out of application source code.

Environment variables:

DATABASE_URL
SECRET_KEY

are loaded from:

.env

The repository contains:

.env.example

with placeholder values.

.env is excluded through .gitignore.

Alembic also reads the database URL from the environment.

AI-Assisted Development

AI assistance was used throughout the project.

AI was used for:

Understanding the capstone requirements
Discussing architecture and implementation approaches
Generating initial code structures
Debugging Python and FastAPI errors
Debugging database and migration issues
Creating automated tests
Improving validation and error handling
Drafting documentation
Reviewing implementation against the capstone requirements

AI-generated code was not accepted blindly.

The implementation was:

Run locally
Tested through the API
Tested through the customer website
Tested through the dashboard
Tested against PostgreSQL
Tested using automated pytest tests
Debugged when errors occurred

The final project structure and implementation decisions were reviewed during development.

Important Development Decisions
FastAPI

FastAPI was selected because the capstone explicitly supports Python/FastAPI and it provides convenient request validation, routing, dependency injection, and background tasks.

PostgreSQL

PostgreSQL was selected for real persistence and tenant-isolation requirements.

Docker

Docker was used to provide a reproducible local PostgreSQL environment.

Console Notification

A console-based notification was intentionally used instead of a paid email provider.

This keeps the project within the capstone's free/local development scope while still demonstrating the background-job architecture.

Deterministic Geo Tests

External geo providers are difficult to reliably test by intentionally taking them offline.

Therefore, the geo provider functions are mocked in automated tests to deterministically verify:

Provider A → success
Provider A → failure → Provider B
Both → failure
Current Verification

Automated tests currently cover:

4 geo tests
1 notification retry test

Total:

5 passed

Additional manual verification covered:

PostgreSQL connectivity
Alembic migrations
Authentication
Widget CRUD
Widget rendering
Cross-origin widget loading
Lead submission
Dashboard submission display
Rate limiting
Widget caching/version headers
Environment-based configuration
Remaining Development / Production Considerations

The current implementation is intended for the capstone's local evaluation scope.

Potential production improvements include:

Redis-backed distributed rate limiting
Production email provider or queue
Dedicated worker process
More sophisticated spam detection
Production-grade secret management
HTTPS
Stronger CSP configuration
Production deployment
More comprehensive automated API integration tests

These are outside the current local capstone scope unless specifically required.