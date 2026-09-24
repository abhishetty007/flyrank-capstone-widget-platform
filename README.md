# FlyRank Embeddable Widget & Lead-Capture Platform

A FastAPI-based embeddable widget platform that allows website owners to create widgets, embed them on external websites, collect visitor submissions, protect the public submission endpoint, enrich submissions with geographic information, and view collected leads through a dashboard.

## Project Overview

This project implements the FlyRank Backend AI Engineering Capstone:

**Embeddable Widget & Lead-Capture Platform**

The platform supports two main actors:

- **Widget Owner** — creates and manages widgets and views collected submissions.
- **Website Visitor** — interacts with an embedded widget and submits information.

The system is designed around a multi-tenant architecture where authenticated owners can only access their own widgets and submissions.

---

## Architecture

```text
                    ┌──────────────────────┐
                    │     Widget Owner     │
                    └──────────┬───────────┘
                               │ JWT
                               ▼
                    ┌──────────────────────┐
                    │   FastAPI Backend    │
                    │                      │
                    │ Auth / Widget API    │
                    │ Dashboard API        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     PostgreSQL       │
                    │                      │
                    │ Users                │
                    │ Widgets              │
                    │ Submissions          │
                    │ Notification Jobs    │
                    └──────────────────────┘


 Customer Website
 ┌──────────────────────────────┐
 │                              │
 │     Embedded widget.js       │
 │             │                │
 └─────────────┼────────────────┘
               │
               ▼
       Public Submission API
               │
               ▼
       Request Size Validation
               │
               ▼
          Rate Limiting
               │
               ▼
           Honeypot
               │
               ▼
          Idempotency
               │
               ▼
         Geo Enrichment
          │          │
       Provider A  Provider B
          │          │
          └────┬─────┘
               ▼
           PostgreSQL
               │
               ▼
       Background Notification
          Job + Retries

          Features
Authentication
User registration
User login
JWT authentication
Password hashing using bcrypt
Protected owner APIs
Widget Management

Authenticated owners can:

Create widgets
List their widgets
Retrieve individual widgets
Update widgets
Delete widgets

Each widget has:

Public ID
Type
Title
Description
Configurable fields
Button text
Display options
Version
Multi-Tenant Isolation

Widget and dashboard queries are scoped to the authenticated owner.

An owner cannot access another owner's widgets or submissions through the authenticated API.

Embeddable Widget

A customer website can embed the widget using:

<script
    src="http://127.0.0.1:8000/widget/widget.js"
    data-widget-id="YOUR_PUBLIC_WIDGET_ID">
</script>

The widget dynamically loads its configuration from the backend and renders the form.

Public Submission API

Visitors submit data through:

POST /public/submissions

The submission path includes:

Request-size validation
Widget validation
IP-based rate limiting
Honeypot filtering
Idempotency protection
Geo enrichment
Database persistence
Background notification job
Abuse Protection

The public submission endpoint includes:

Request-size limit
Rate limiting
Honeypot field
Idempotency keys
Validation through Pydantic
Restricted CORS configuration
Geo Enrichment

The system attempts geographic enrichment using two providers.

ip-api.com
     │
     ├── success → use result
     │
     └── failure
           ↓
       ipapi.co
           │
           ├── success → use result
           │
           └── failure → continue without geo

A geo provider failure does not prevent the lead from being stored.

Background Notification Job

After a successful submission, a notification job is created.

The job supports:

Background processing
Up to 3 attempts
Retry handling
Failure status
Error storage
Failure alert through application logging

The current development implementation prints the notification to the backend console.

Technology Stack
Backend
Python
FastAPI
SQLAlchemy
Pydantic
Alembic
PostgreSQL
JWT
bcrypt
Infrastructure
Docker
Docker Compose
Frontend / Widget
HTML
JavaScript
CSS
External Services
ip-api.com
ipapi.co

No paid API or credit card is required for the local development setup.

Project Structure
flyrank-capstone-widget-platform/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── widgets.py
│   │   │   ├── submissions.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── core/
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── rate_limit.py
│   │   │
│   │   ├── models/
│   │   │   └── __init__.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── widget.py
│   │   │   └── submission.py
│   │   │
│   │   ├── services/
│   │   │   ├── geo.py
│   │   │   └── notifications.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── test_geo.py
│   │   └── test_notifications.py
│   │
│   └── requirements.txt
│
├── customer-site/
│   ├── index.html
│   └── dashboard.html
│
├── docs/
│   └── design.md
│
├── migrations/
│
├── widget/
│   └── widget.js
│
├── .env.example
├── .gitignore
├── BUILDLOG.md
├── EVIDENCE.md
├── README.md
├── capstone.yaml
└── docker-compose.yml
Prerequisites

Install:

Python 3.13+
Docker Desktop
Git

Verify:

python --version
docker --version
docker compose version
git --version
Setup
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd flyrank-capstone-widget-platform
2. Create the Python virtual environment
python -m venv backend\.venv

Activate it:

.\backend\.venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r backend\requirements.txt
4. Configure environment variables

Create:

.env

Use:

DATABASE_URL=postgresql+psycopg2://flyrank:postgres@127.0.0.1:5433/flyrank
SECRET_KEY=replace-with-a-random-secret

Do not commit .env.

The repository contains .env.example as a template.

Start PostgreSQL

Start the Docker database:

docker compose up -d

Check:

docker ps

The PostgreSQL container is exposed on:

127.0.0.1:5433
Run Database Migrations
alembic upgrade head

Check migration status:

alembic current
Start the FastAPI Backend

From the project root:

uvicorn backend.app.main:app --reload

Backend:

http://127.0.0.1:8000

Health check:

http://127.0.0.1:8000/health

Swagger documentation:

http://127.0.0.1:8000/docs
Run the Customer Website

Open another terminal.

From the project root:

python -m http.server 5500 --directory customer-site

Customer site:

http://127.0.0.1:5500

This intentionally uses a different origin from the FastAPI server to exercise CORS.

Using the Platform
1. Register

Create an owner account through:

POST /auth/register
2. Login

Login through:

POST /auth/login

The response contains a JWT access token.

3. Create a Widget

Create a widget through:

POST /widgets/

Example configuration:

{
  "widget_type": "signup",
  "title": "Get in Touch",
  "description": "Send us your details.",
  "fields": {
    "name": "text",
    "email": "email"
  },
  "button_text": "Submit",
  "display_options": {}
}
4. Embed the Widget

Use the widget's public ID:

<script
    src="http://127.0.0.1:8000/widget/widget.js"
    data-widget-id="YOUR_PUBLIC_WIDGET_ID">
</script>
5. Submit a Lead

A visitor can fill in the embedded form.

The submission is sent to:

POST /public/submissions
6. View Submissions

Open:

http://127.0.0.1:5500/dashboard.html

Login using the owner credentials.

The dashboard displays collected submissions and geographic information when available.

Testing

Run the complete test suite:

$env:PYTHONPATH="."
pytest -v

The test suite covers:

Geo fallback
Provider A success
Provider A failure → Provider B fallback
Both providers unavailable
Private IP handling
Notification reliability
Notification failure
Three retry attempts
Failed job state
Failure alert
Security Considerations

The platform implements several security boundaries:

JWT authentication for owner APIs
bcrypt password hashing
Owner-scoped database queries
Restricted CORS origins
Public/private API separation
Rate limiting
Honeypot spam protection
Request-size limits
Idempotency protection
Input validation
Secrets loaded from environment variables

The .env file is excluded from Git.

Widget Delivery

The widget bundle is served through:

GET /widget/widget.js

The response includes:

Cache-Control: public, max-age=300, must-revalidate
X-Widget-Version: 1

This allows browser/proxy caching while exposing an explicit widget bundle version.

Database

PostgreSQL stores:

Users
Widgets
Submissions
Notification jobs

Alembic manages schema migrations.

The submission table includes a unique constraint for:

(widget_id, idempotency_key)

This prevents duplicate submissions when the same idempotency key is reused.

Current Development Scope

The project intentionally keeps the widget UI minimal.

The notification side effect currently uses console output rather than a production email provider.

This keeps the project within the free/local development scope while demonstrating the required background-job and failure-handling architecture.

AI-Assisted Development

AI assistance was used during development for:

Architecture discussion
Code generation
Debugging
Test creation
Documentation drafting
Error diagnosis

The final implementation was manually tested and verified through the project's API, customer website, dashboard, database, and automated tests.

Development decisions and AI assistance are documented further in BUILDLOG.md.

License

This project was created as part of the FlyRank Backend AI Engineering Capstone.