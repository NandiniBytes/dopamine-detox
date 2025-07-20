from fastapi import APIRouter, Depends, Body
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.user import User
from app.models.activity import CoachInteraction
from .users import get_current_user
from app.services.llm_service import generate_coach_response
from typing import List
from pydantic import BaseModel

router = APIRouter()

class CoachMessage(BaseModel):
    message: str

@router.post("/chat", response_model=str)
async def chat_with_coach(
    request: CoachMessage,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Send a message to the AI coach and get a response.
    Maintains conversation history for context.
    """
    # Fetch recent conversation history (e.g., last 10 messages)
    history_res = await session.execute(
        select(CoachInteraction)
        .where(CoachInteraction.user_id == current_user.id)
        .order_by(CoachInteraction.timestamp.desc())
        .limit(10)
    )
    history = history_res.scalars().all()
    # Reverse to get chronological order for the LLM
    history.reverse() 
    
    history_for_llm = [{"user_message": h.user_message, "ai_response": h.ai_response} for h in history]

    ai_response = generate_coach_response(history_for_llm, request.message)

    # Save the new interaction
    new_interaction = CoachInteraction(
        user_id=current_user.id,
        user_message=request.message,
        ai_response=ai_response
    )
    session.add(new_interaction)
    await session.commit()

    return ai_response