from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.core.database import get_db
from backend.app.models import Submission, User, Widget


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/submissions")
def list_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissions = (
        db.query(Submission)
        .join(Widget, Submission.widget_id == Widget.id)
        .filter(
            Widget.owner_id == current_user.id,
        )
        .order_by(
            Submission.created_at.desc(),
        )
        .all()
    )

    return [
        {
            "id": submission.id,
            "widget_id": submission.widget_id,
            "payload": submission.payload,
            "ip_address": submission.ip_address,
            "country": submission.country,
            "city": submission.city,
            "geo_provider": submission.geo_provider,
            "created_at": submission.created_at,
        }
        for submission in submissions
    ]


@router.get("/submissions/{submission_id}")
def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission = (
        db.query(Submission)
        .join(Widget, Submission.widget_id == Widget.id)
        .filter(
            Submission.id == submission_id,
            Widget.owner_id == current_user.id,
        )
        .first()
    )

    if submission is None:
        raise HTTPException(
            status_code=404,
            detail="Submission not found",
        )

    return {
        "id": submission.id,
        "widget_id": submission.widget_id,
        "payload": submission.payload,
        "ip_address": submission.ip_address,
        "country": submission.country,
        "city": submission.city,
        "geo_provider": submission.geo_provider,
        "created_at": submission.created_at,
    }