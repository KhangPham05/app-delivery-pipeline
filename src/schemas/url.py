from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class UrlCreate(BaseModel):
    original_url: HttpUrl


class UrlOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    short_code: str
    original_url: str
    created_at: datetime
