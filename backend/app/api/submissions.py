from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal, get_db
from backend.app.core.rate_limit import check_rate_limit
from backend.app.models import Submission, Widget
from backend.app.schemas.submission import SubmissionCreate
from backend.app.services.geo import get_geo_location
from backend.app.services.notifications import (
    create_notification_job,
    process_notification_job,
)

router = APIRouter(prefix="/public", tags=["Public Submissions"])

MAX_REQUEST_SIZE = 10 * 1024  # 10 KB


def run_notification_job(job_id: int):
    db = SessionLocal()
    try:
        process_notification_job(db, job_id)
    finally:
        db.close()


@router.post("/submissions", status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission_data: SubmissionCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Reject oversized request bodies.
    content_length = request.headers.get("content-length")

    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="Submission payload is too large.",
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid Content-Length header.",
            )

    widget = (
        db.query(Widget)
        .filter(Widget.public_id == submission_data.widget_id)
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    client_ip = "unknown"

    if request.client:
        client_ip = request.client.host

    rate_limit_key = f"{client_ip}:{widget.id}"

    if not check_rate_limit(rate_limit_key):
        raise HTTPException(
            status_code=429,
            detail="Too many submissions. Please try again later.",
        )

    # Honeypot: silently accept but do not store the submission.
    if submission_data.honeypot:
        return {
            "status": "accepted",
            "message": "Submission received",
        }

    # Idempotency check.
    if submission_data.idempotency_key:
        existing_submission = (
            db.query(Submission)
            .filter(
                Submission.widget_id == widget.id,
                Submission.idempotency_key
                == submission_data.idempotency_key,
            )
            .first()
        )

        if existing_submission:
            return {
                "status": "duplicate",
                "message": "Submission already received",
                "submission_id": existing_submission.id,
            }

    # Geo enrichment.
    geo_data = None

    if client_ip != "unknown":
        geo_data = get_geo_location(client_ip)

    country = None
    city = None
    geo_provider = None

    if geo_data:
        country = geo_data.get("country")
        city = geo_data.get("city")
        geo_provider = geo_data.get("provider")

    # Store submission.
    submission = Submission(
        widget_id=widget.id,
        idempotency_key=submission_data.idempotency_key,
        payload=submission_data.data,
        ip_address=client_ip,
        country=country,
        city=city,
        geo_provider=geo_provider,
    )

    db.add(submission)

    try:
        db.commit()
        db.refresh(submission)

    except IntegrityError:
        db.rollback()

        # Handle concurrent duplicate submissions.
        if submission_data.idempotency_key:
            existing_submission = (
                db.query(Submission)
                .filter(
                    Submission.widget_id == widget.id,
                    Submission.idempotency_key
                    == submission_data.idempotency_key,
                )
                .first()
            )

            if existing_submission:
                return {
                    "status": "duplicate",
                    "message": "Submission already received",
                    "submission_id": existing_submission.id,
                }

        raise HTTPException(
            status_code=409,
            detail="Could not process submission",
        )

    # Create notification job only after successful persistence.
    job = create_notification_job(
        db=db,
        submission=submission,
    )

    # Run notification processing in the background.
    background_tasks.add_task(
        run_notification_job,
        job.id,
    )

    return {
        "status": "success",
        "message": "Submission received",
        "submission_id": submission.id,
        "notification_job_id": job.id,
        "geo": {
            "country": country,
            "city": city,
            "provider": geo_provider,
        },
    }