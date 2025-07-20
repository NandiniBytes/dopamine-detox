from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.user import User
from app.models.activity import JournalEntry
from app.schemas.journal import JournalEntryCreate, JournalEntryOut
from app.services.llm_service import generate_journal_reflection
from .users import get_current_user
from typing import List

router = APIRouter()

@router.post("/", response_model=JournalEntryOut, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new journal entry.
    An LLM-powered reflection is generated and saved with the entry.
    """
    # Generate reflection using the LLM service
    reflection_text = generate_journal_reflection(entry.content, entry.mood_vibe)

    new_entry = JournalEntry(
        **entry.model_dump(),
        user_id=current_user.id,
        reflection=reflection_text
    )
    session.add(new_entry)
    await session.commit()
    await session.refresh(new_entry)
    return new_entry

@router.get("/", response_model=List[JournalEntryOut])
async def get_journal_entries(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all journal entries for the current user.
    """
    result = await session.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    entries = result.scalars().all()
    return entries
