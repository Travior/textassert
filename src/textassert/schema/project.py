from pydantic import BaseModel, Field
from pathlib import Path

PROJECT_FILENAME = Path(".textassert")
SETTINGS_FILEPATH = Path.home() / Path(".textassert/settings.json")

class Feedback(BaseModel):
    quote: str = Field(...)
    feedback: str = Field(...)

class CriterionResponse(BaseModel):
    passed: bool = Field(...)
    feedbacks: list[Feedback] = Field(description="A list of feedbacks on the text. If there are no issues, return an empty list. This can NEVER be null.")

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