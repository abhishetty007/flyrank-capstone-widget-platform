import time

from sqlalchemy.orm import Session

from backend.app.models import NotificationJob, Submission

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1


def create_notification_job(
    db: Session,
    submission: Submission,
) -> NotificationJob:
    job = NotificationJob(
        submission_id=submission.id,
        status="pending",
        attempts=0,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def send_notification(submission: Submission) -> None:
    """
    Development notification.

    For the capstone this represents the side effect.
    It can later be replaced with email, Mailpit, or a webhook.
    """
    print(
        "Notification:",
        {
            "submission_id": submission.id,
            "payload": submission.payload,
        },
    )


def process_notification_job(
    db: Session,
    job_id: int,
) -> NotificationJob | None:
    job = (
        db.query(NotificationJob)
        .filter(NotificationJob.id == job_id)
        .first()
    )

    if job is None:
        return None

    submission = (
        db.query(Submission)
        .filter(Submission.id == job.submission_id)
        .first()
    )

    if submission is None:
        job.status = "failed"
        job.last_error = "Submission not found"

        db.commit()
        db.refresh(job)

        print(
            f"ALERT: Notification job {job.id} failed: "
            "submission not found."
        )

        return job

    while job.attempts < MAX_ATTEMPTS:
        job.attempts += 1

        try:
            send_notification(submission)

            job.status = "completed"
            job.last_error = None

            db.commit()
            db.refresh(job)

            return job

        except Exception as exc:
            job.last_error = str(exc)

            db.commit()

            print(
                f"Notification attempt {job.attempts}/"
                f"{MAX_ATTEMPTS} failed: {exc}"
            )

            if job.attempts < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    job.status = "failed"

    db.commit()
    db.refresh(job)

    print(
        f"ALERT: Notification job {job.id} failed after "
        f"{MAX_ATTEMPTS} attempts."
    )

    return job