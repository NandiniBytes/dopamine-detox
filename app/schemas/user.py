from pydantic import BaseModel, EmailStr
import uuid
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class UserProgress(BaseModel):
    total_journal_entries: int
    completed_challenges: int
    current_streak: int


# app/schemas/journal.py
from pydantic import BaseModel
import uuid
from datetime import datetime

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
