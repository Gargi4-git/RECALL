
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_id: UUID
    original_filename: str
    mime_type: str
    file_size_bytes: int
    status: str
    uploaded_at: datetime
