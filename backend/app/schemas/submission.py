from typing import Any, Optional

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    widget_id: str = Field(
        min_length=1,
        max_length=64,
    )

    data: dict[str, Any] = Field(
        default_factory=dict,
    )

    honeypot: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    idempotency_key: Optional[str] = Field(
        default=None,
        max_length=255,
    )