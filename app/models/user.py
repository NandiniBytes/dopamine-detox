from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional, TYPE_CHECKING
import uuid
from datetime import datetime

# This block is only for type checking (e.g., by Pylance)
# It is not executed at runtime, which avoids circular import errors.
if TYPE_CHECKING:
    from .activity import JournalEntry, Habit, DetoxChallenge, CoachInteraction

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    journal_entries: List["JournalEntry"] = Relationship(back_populates="user")
    habits: List["Habit"] = Relationship(back_populates="user")
    detox_challenges: List["DetoxChallenge"] = Relationship(back_populates="user")
    coach_interactions: List["CoachInteraction"] = Relationship(back_populates="user")

