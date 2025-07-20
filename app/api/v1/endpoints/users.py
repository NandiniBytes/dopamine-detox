from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.security import oauth2_scheme, verify_token
from app.models.user import User
from app.models.activity import JournalEntry, DetoxChallenge
from app.schemas.user import UserOut, UserProgress
import uuid

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token, credentials_exception)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = await session.get(User, uuid.UUID(user_id))
    if user is None:
        raise credentials_exception
    return user

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user's details.
    """
    return current_user

@router.get("/me/progress", response_model=UserProgress)
async def get_user_progress(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """
    Get progress metrics for the current user.
    """
    journal_count_res = await session.execute(select(func.count(JournalEntry.id)).where(JournalEntry.user_id == current_user.id))
    journal_count = journal_count_res.scalar_one()

    challenge_count_res = await session.execute(
        select(func.count(DetoxChallenge.id)).where(DetoxChallenge.user_id == current_user.id, DetoxChallenge.is_completed == True)
    )
    challenge_count = challenge_count_res.scalar_one()
    
    # Streak logic would be more complex, this is a placeholder
    current_streak = 5 # Placeholder

    return UserProgress(
        total_journal_entries=journal_count,
        completed_challenges=challenge_count,
        current_streak=current_streak
    )
