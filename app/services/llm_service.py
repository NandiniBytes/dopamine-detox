# app/services/llm_service.py
# Service for interacting with the Groq LLM.

from groq import Groq
from app.core.config import settings
from typing import List, Dict

client = None

def initialize_llm():
    """Initializes the Groq client."""
    global client
    if settings.GROQ_API_KEY:
        client = Groq(api_key=settings.GROQ_API_KEY)
    else:
        print("WARNING:  GROQ_API_KEY not found. LLM features will be disabled.")

def get_llm_completion(prompt: str, max_tokens: int = 1024) -> str:
    """
    Gets a completion from the Groq LLM.
    """
    if not client:
        return "LLM service is not available."
        
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and empathetic AI assistant for the Dopamine Detox app. Your tone is gentle, encouraging, and science-informed.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=settings.LLM_MODEL_NAME,
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "An error occurred while generating the response."

def generate_journal_reflection(entry_content: str, mood: str) -> str:
    prompt = f"""
    A user has submitted a journal entry. Analyze the content and their stated mood to provide a gentle, insightful, and actionable reflection.
    The goal is to help them understand their feelings without being prescriptive. Offer a single, simple insight.

    User's Mood: "{mood}"
    Journal Entry: "{entry_content}"

    Based on this, provide a short, one-paragraph reflection.
    """
    return get_llm_completion(prompt, max_tokens=256)

def generate_daily_challenge(journal_summary: str, habits: List[str]) -> Dict[str, str]:
    habit_list = ", ".join(habits) if habits else "general digital usage"
    prompt = f"""
    Based on the user's recent emotional state and habits, create a personalized, low-dopamine "detox" challenge for the day.
    The challenge should be specific, achievable, and positive. Frame it as an invitation, not a command.

    User's recent context: {journal_summary}
    User's logged high-dopamine habits: {habit_list}

    Example format:
    Title: "Mindful Morning"
    Description: "Instead of checking your phone first thing, spend 5 minutes stretching and noticing how your body feels."

    Generate one challenge with a 'title' and a 'description'. Return it as a simple JSON object with keys "title" and "description".
    """
    # This is a simplified approach. For robust JSON, you'd use function calling/tool use if the model supports it.
    response_text = get_llm_completion(prompt, max_tokens=200)
    try:
        # A simple parser for the "key: value" format
        lines = response_text.strip().split('\n')
        title = lines[0].split(':', 1)[1].strip().strip('"')
        description = lines[1].split(':', 1)[1].strip().strip('"')
        return {"title": title, "description": description}
    except Exception:
        return {"title": "A Moment of Peace", "description": "Take 5 minutes today to simply sit without any screens and listen to your surroundings."}

def generate_coach_response(history: List[Dict[str, str]], user_message: str) -> str:
    # Build a history for the LLM
    messages = [
        {
            "role": "system",
            "content": "You are a gentle, non-judgmental accountability coach. Your goal is to help the user stick to their detox goals. You have memory of past conversations. Keep your responses concise and encouraging."
        }
    ]
    for interaction in history:
        messages.append({"role": "user", "content": interaction['user_message']})
        messages.append({"role": "assistant", "content": interaction['ai_response']})
    
    messages.append({"role": "user", "content": user_message})

    # We don't need to pass the whole prompt here, just the messages
    if not client:
        return "LLM service is not available."
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=settings.LLM_MODEL_NAME,
            temperature=0.5,
            max_tokens=200,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "I'm having a little trouble connecting right now. Let's try again in a moment."
