# ... (imports remain the same)
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.database import get_session
from app.models.user import User
from app.models.activity import Habit
from .users import get_current_user
from typing import List, Dict, Any
from datetime import date, timedelta
from app.services.habit_analyzer import analyze_digital_habits # Import the analyzer

router = APIRouter()

@router.post("/log", status_code=201)
async def log_habit_data(
    data: List[Dict[str, Any]] = Body(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # ... (logging logic remains the same)
    today = date.today()
    for habit_data in data:
        new_habit = Habit(
            user_id=current_user.id,
            name=habit_data.get("name"),
            type=habit_data.get("type"),
            data=habit_data.get("data", {}),
            recorded_at=today
        )
        session.add(new_habit)
    
    await session.commit()
    return {"message": "Habit data logged successfully."}

@router.get("/analysis", response_model=Dict[str, Any])
async def get_habit_analysis(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Analyzes the user's digital habits from the last 7 days.
    """
    seven_days_ago = date.today() - timedelta(days=7)
    result = await session.execute(
        select(Habit)
        .where(Habit.user_id == current_user.id)
        .where(Habit.recorded_at >= seven_days_ago)
    )
    habits = result.scalars().all()
    
    analysis = analyze_digital_habits(habits)
    return analysis