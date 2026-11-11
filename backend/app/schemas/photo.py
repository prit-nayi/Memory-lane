import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    visitor_id: uuid.UUID
    original_filename: str
    content_type: str
    file_size: int
    status: Literal["pending", "approved", "rejected"]
    created_at: datetime
    updated_at: datetime
