from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: UUID
    file_path: str
    project_id: UUID

    model_config = ConfigDict(from_attributes=True)