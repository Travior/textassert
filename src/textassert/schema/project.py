from pydantic import BaseModel
from pathlib import Path

PROJECT_FILENAME = Path(".textassert")
SETTINGS_FILEPATH = Path.home() / Path(".textassert/settings.json")

class Feedback(BaseModel):
    quote: str
    feedback: str

class CriterionResponse(BaseModel):
    passed: bool
    feedbacks: list[Feedback]

class Criterion(BaseModel):
    name: str
    description: str
    passed: bool
    feedbacks: list[Feedback]

class Project(BaseModel):
    file: str
    criteria: list[Criterion]

class ProjectFile(BaseModel):
    projects: list[Project]


class Settings(BaseModel):
    openrouter_api_key: str