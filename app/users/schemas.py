from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    joined_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)