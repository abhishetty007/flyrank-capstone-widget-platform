from typing import Optional

from pydantic import BaseModel, Field


class WidgetCreate(BaseModel):
    widget_type: str = Field(
        default="signup",
        max_length=50,
    )
    title: str = Field(
        min_length=1,
        max_length=255,
    )
    description: Optional[str] = None
    fields: dict = {}
    button_text: str = Field(
        default="Submit",
        max_length=100,
    )
    display_options: dict = {}


class WidgetUpdate(BaseModel):
    widget_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: Optional[str] = None
    fields: Optional[dict] = None
    button_text: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    display_options: Optional[dict] = None