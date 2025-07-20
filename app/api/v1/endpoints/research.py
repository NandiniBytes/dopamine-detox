# Endpoint for querying the RAG system.

from fastapi import APIRouter, Depends, Query
from app.models.user import User
from .users import get_current_user
from app.services.rag_service import query_rag

router = APIRouter()

@router.get("/query", response_model=str)
async def ask_research_question(
    query: str = Query(..., min_length=3, max_length=100, description="Your question about digital wellbeing or minimalism."),
    current_user: User = Depends(get_current_user) # Ensures only authenticated users can query
):
    """

    Ask a question to the research-backed knowledge base (RAG).
    The system will retrieve relevant information and generate a synthesized answer.
    """
    answer = query_rag(query)
    return answer
