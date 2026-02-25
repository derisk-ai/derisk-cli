"""App/Agent models for OpenDerisk CLI."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GptsApp(BaseModel):
    """Agent instance model."""

    app_code: Optional[str] = None
    app_name: Optional[str] = None
    app_describe: Optional[str] = None
    team_mode: Optional[str] = None
    published: Optional[bool] = False
    user_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GptsAppResponse(BaseModel):
    """App list response."""

    total_count: int = 0
    total_page: int = 0
    current_page: int = 0
    page_size: int = 20
    app_list: list[GptsApp] = Field(default_factory=list)
