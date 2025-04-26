from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class LeadState(str, Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"


class Lead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    state: LeadState = LeadState.PENDING
    resume_path: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
