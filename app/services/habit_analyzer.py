# Service to analyze user habits and detect patterns.

from typing import List, Dict, Any
from collections import Counter
from app.models.activity import Habit
from app.services.llm_service import get_llm_completion

def analyze_digital_habits(habits: List[Habit]) -> Dict[str, Any]:
    """
    Analyzes a list of digital habits to find patterns and generate insights.
    """
    if not habits:
        return {
            "summary": "Not enough habit data to analyze. Keep logging your screen time!",
            "top_apps": [],
            "total_screen_time_minutes": 0
        }

    screen_time_data = []
    for habit in habits:
        if habit.type == 'digital' and 'minutes_spent' in habit.data:
            screen_time_data.append({
                "name": habit.name,
                "minutes": habit.data['minutes_spent']
            })

    if not screen_time_data:
        return {
            "summary": "No digital screen time data found.",
            "top_apps": [],
            "total_screen_time_minutes": 0
        }

    # Calculate total screen time
    total_minutes = sum(item['minutes'] for item in screen_time_data)

    # Find top 3 most used apps
    app_counter = Counter()
    for item in screen_time_data:
        app_counter[item['name']] += item['minutes']
    
    top_apps = [{"app": name, "minutes": minutes} for name, minutes in app_counter.most_common(3)]

    # Generate LLM-powered insight
    insight_prompt = f"""
    A user's recent digital habits show a total screen time of {total_minutes} minutes.
    Their most used apps are: {', '.join([app['app'] for app in top_apps])}.

    Based on this data, provide a short, non-judgmental insight about their potential habit loop.
    For example, identify a potential cue (e.g., boredom, stress) that might lead to the routine (opening these apps).
    Keep it to 1-2 sentences.
    
    Example: "It seems like you often turn to these apps for quick entertainment. Consider if this happens most when you're feeling bored or transitioning between tasks."
    """
    llm_summary = get_llm_completion(insight_prompt, max_tokens=150)

    return {
        "summary": llm_summary,
        "top_apps": top_apps,
        "total_screen_time_minutes": total_minutes
    }
