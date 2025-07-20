from pydantic import BaseModel
from typing import List

class Recommendation(BaseModel):
    activity_name: str
    description: str
    category: str # e.g., "Creative", "Outdoor", "Mindfulness"