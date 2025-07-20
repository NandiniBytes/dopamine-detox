from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

class JournalEntryCreate(BaseModel):
    content: str
    mood_vibe: str

class JournalEntryOut(BaseModel):
    id: uuid.UUID
    content: str
    mood_vibe: str
    reflection: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
