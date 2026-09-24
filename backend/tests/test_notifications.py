from unittest.mock import patch

from backend.app.models import NotificationJob, Submission
from backend.app.services.notifications import (
    MAX_ATTEMPTS,
    process_notification_job,
)


class FakeQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.result


class FakeDB:
    def __init__(self, job, submission):
        self.job = job
        self.submission = submission
        self.commit_count = 0

    def query(self, model):
        if model is NotificationJob:
            return FakeQuery(self.job)

        if model is Submission:
            return FakeQuery(self.submission)

        return FakeQuery(None)

    def commit(self):
        self.commit_count += 1

    def refresh(self, obj):
        pass


def test_notification_retries_three_times_then_fails():
    job = NotificationJob(
        id=1,
        submission_id=1,
        status="pending",
        attempts=0,
    )

    submission = Submission(
        id=1,
        payload={
            "name": "Test User",
            "email": "test@example.com",
        },
    )

    db = FakeDB(
        job=job,
        submission=submission,
    )

    with patch(
        "backend.app.services.notifications.send_notification",
        side_effect=Exception("Notification service unavailable"),
    ) as mock_notification:

        result = process_notification_job(
            db=db,
            job_id=1,
        )

    assert result is job
    assert result.status == "failed"
    assert result.attempts == MAX_ATTEMPTS
    assert result.last_error == "Notification service unavailable"

    assert mock_notification.call_count == MAX_ATTEMPTS