import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Updated to include the new 'research' endpoint
from app.api.v1.endpoints import auth, users, journal, habits, recommendations, coach, research
from app.core.database import create_db_and_tables
from app.core.config import settings
from app.services.llm_service import initialize_llm
from app.services.rag_service import initialize_rag_service

# Lifespan manager for application startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    - Creates database and tables on startup.
    - Initializes the LLM client.
    - Initializes the RAG service (loads/builds the vector index).
    """
    print("INFO:     Starting up Dopamine Detox backend...")
    create_db_and_tables()
    initialize_llm()
    initialize_rag_service() # New: Initialize RAG service on startup
    print("INFO:     Application startup complete.")
    yield
    print("INFO:     Shutting down Dopamine Detox backend...")
    # Clean up resources if needed on shutdown
    print("INFO:     Application shutdown complete.")


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend for Dopamine Detox, a productivity and mental health app.",
    version="0.2.0", # Version updated
    lifespan=lifespan
)

# CORS (Cross-Origin Resource Sharing) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(journal.router, prefix="/api/v1/journal", tags=["Journaling"])
app.include_router(habits.router, prefix="/api/v1/habits", tags=["Habits & Screen Time"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(coach.router, prefix="/api/v1/coach", tags=["AI Coach"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research (RAG)"]) # New router

@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Dopamine Detox API! Now with RAG support."}

# To run the app: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
