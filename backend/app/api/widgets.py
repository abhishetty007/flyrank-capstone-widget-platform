from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.core.database import get_db
from backend.app.models import User, Widget
from backend.app.schemas.widget import WidgetCreate, WidgetUpdate


router = APIRouter(
    prefix="/widgets",
    tags=["Widgets"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_widget(
    widget_data: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = Widget(
        owner_id=current_user.id,
        public_id=uuid4().hex,
        widget_type=widget_data.widget_type,
        title=widget_data.title,
        description=widget_data.description,
        fields=widget_data.fields,
        button_text=widget_data.button_text,
        display_options=widget_data.display_options,
        version=1,
    )

    db.add(widget)
    db.commit()
    db.refresh(widget)

    return widget


@router.get("/")
def list_widgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widgets = (
        db.query(Widget)
        .filter(Widget.owner_id == current_user.id)
        .all()
    )

    return widgets


@router.get("/{widget_id}")
def get_widget(
    widget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = (
        db.query(Widget)
        .filter(
            Widget.id == widget_id,
            Widget.owner_id == current_user.id,
        )
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return widget


@router.put("/{widget_id}")
def update_widget(
    widget_id: int,
    widget_data: WidgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = (
        db.query(Widget)
        .filter(
            Widget.id == widget_id,
            Widget.owner_id == current_user.id,
        )
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    update_data = widget_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(widget, field, value)

    widget.version += 1

    db.commit()
    db.refresh(widget)

    return widget


@router.delete("/{widget_id}")
def delete_widget(
    widget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = (
        db.query(Widget)
        .filter(
            Widget.id == widget_id,
            Widget.owner_id == current_user.id,
        )
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    db.delete(widget)
    db.commit()

    return {
        "message": "Widget deleted successfully",
    }
@router.get("/public/{public_id}")
def get_public_widget(
    public_id: str,
    db: Session = Depends(get_db),
):
    widget = (
        db.query(Widget)
        .filter(
            Widget.public_id == public_id,
        )
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return {
        "public_id": widget.public_id,
        "widget_type": widget.widget_type,
        "title": widget.title,
        "description": widget.description,
        "fields": widget.fields,
        "button_text": widget.button_text,
        "display_options": widget.display_options,
        "version": widget.version,
    }