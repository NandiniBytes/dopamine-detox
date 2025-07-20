# app/core/database.py (CORRECTED)
# Database connection and session management.

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine as create_sync_engine
from .config import settings

# Using async engine for FastAPI
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def create_db_and_tables():
    """
    Creates the database and all tables defined in the models.
    This is a synchronous operation, so we use a sync engine.
    """
    # We need a synchronous engine to create tables.
    # The DATABASE_URL for a sync engine should not have the "+asyncpg" part.
    sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
    sync_engine = create_sync_engine(sync_db_url)
    
    # Import all models here so they are registered with SQLModel's metadata
    # This is a crucial step!
    from app.models.user import User
    from app.models.activity import JournalEntry, Habit, DetoxChallenge, CoachInteraction
    
    # This will now work correctly
    SQLModel.metadata.create_all(sync_engine)


from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a database session for each request.
    """
    async with async_session() as session:
        yield session
