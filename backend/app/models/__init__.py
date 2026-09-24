from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    widgets: Mapped[list["Widget"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    public_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    widget_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    fields: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    button_text: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Submit",
    )

    display_options: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        back_populates="widgets",
    )

    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="widget",
        cascade="all, delete-orphan",
    )


class Submission(Base):
    __tablename__ = "submissions"

    __table_args__ = (
        UniqueConstraint(
            "widget_id",
            "idempotency_key",
            name="uq_submission_widget_idempotency",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    widget_id: Mapped[int] = mapped_column(
        ForeignKey("widgets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )

    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    geo_provider: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    widget: Mapped["Widget"] = relationship(
        back_populates="submissions",
    )


class NotificationJob(Base):
    __tablename__ = "notification_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    last_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )