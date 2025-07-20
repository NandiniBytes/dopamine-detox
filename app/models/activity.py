# SQLAlchemy ORM models for activities like journaling, habits, etc.

from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
import uuid
from datetime import datetime, date

# This block is only for type checking (e.g., by Pylance)
if TYPE_CHECKING:
    from .user import User

class JournalEntry(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    content: str
    mood_vibe: str # e.g., "energetic", "calm", "anxious"
    reflection: Optional[str] = None # LLM-generated reflection
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: "User" = Relationship(back_populates="journal_entries")

class Habit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    name: str # e.g., "Social Media Scrolling", "Gaming"
    type: str # "digital" or "physical"
    data: Dict[str, Any] = Field(sa_column=Column(JSONB)) # For screen time, app usage, etc.
    recorded_at: date
    
    user: "User" = Relationship(back_populates="habits")

class DetoxChallenge(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: str
    description: str
    is_completed: bool = Field(default=False)
    created_at: date = Field(default_factory=date.today)
    
    user: "User" = Relationship(back_populates="detox_challenges")

class CoachInteraction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user_message: str
    ai_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="coach_interactions")
