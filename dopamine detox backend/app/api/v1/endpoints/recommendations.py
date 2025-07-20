from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.user import User
from app.models.activity import JournalEntry, DetoxChallenge
from app.schemas.recommendation import Recommendation
from .users import get_current_user
from app.services.llm_service import get_llm_completion
from typing import List
import json
import uuid

router = APIRouter()

@router.get("/detox-challenge", response_model=DetoxChallenge)
async def get_daily_detox_challenge(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Generates and returns a new daily detox challenge for the user.
    If a challenge for today already exists, it returns that one.
    """
    from app.services.llm_service import generate_daily_challenge
    from datetime import date

    today = date.today()
    result = await session.execute(
        select(DetoxChallenge).where(DetoxChallenge.user_id == current_user.id, DetoxChallenge.created_at == today)
    )
    existing_challenge = result.scalars().first()

    if existing_challenge:
        return existing_challenge

    # Fetch recent context for the LLM
    journal_res = await session.execute(
        select(JournalEntry.content, JournalEntry.mood_vibe)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
        .limit(3)
    )
    journals = journal_res.all()
    journal_summary = " ".join([f"Felt '{j.mood_vibe}': {j.content}" for j in journals])

    # In a real app, you'd fetch real habit names
    habits = ["social media", "mindless scrolling"] 

    challenge_data = generate_daily_challenge(journal_summary, habits)
    
    new_challenge = DetoxChallenge(
        user_id=current_user.id,
        title=challenge_data.get("title"),
        description=challenge_data.get("description"),
        created_at=today
    )
    session.add(new_challenge)
    await session.commit()
    await session.refresh(new_challenge)
    return new_challenge

@router.post("/detox-challenge/{challenge_id}/complete", status_code=200)
async def complete_challenge(
    challenge_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    challenge = await session.get(DetoxChallenge, challenge_id)
    if not challenge or challenge.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    challenge.is_completed = True
    session.add(challenge)
    await session.commit()
    return {"message": "Challenge marked as complete!"}


@router.get("/activities", response_model=List[Recommendation])
async def get_low_dopamine_activities(
    vibe: str, # e.g., "creative", "calm", "active"
    current_user: User = Depends(get_current_user)
):
    """
    Recommends low-dopamine activities based on a user's desired vibe.
    """
    prompt = f"""
    A user wants recommendations for low-dopamine activities. Their desired vibe is "{vibe}".
    Based on this, generate a list of 5 activities.
    Categories could include: Creative, Outdoor, Mindfulness, Learning, Social.
    
    Return the list as a JSON array of objects, each with keys "activity_name", "description", and "category".
    Example:
    [
        {{"activity_name": "Nature Journaling", "description": "Go outside and sketch or write about what you see and hear.", "category": "Creative"}},
        {{"activity_name": "Read a Physical Book", "description": "Lose yourself in a story without the distraction of a screen.", "category": "Learning"}}
    ]
    """
    response_str = get_llm_completion(prompt, max_tokens=512)
    try:
        recommendations = json.loads(response_str)
        return recommendations
    except json.JSONDecodeError:
        print(f"Failed to decode LLM JSON response: {response_str}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations.")
