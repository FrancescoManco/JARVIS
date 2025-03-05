from typing import List

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from Jarvis.orchestrator.orchestrator import MultiAgentOrchestrator
from Jarvis.subjective.data.data_generation import email_generation

router = APIRouter()
orchestrator = MultiAgentOrchestrator()

class UserInput(BaseModel):
    message: str

@router.post("/email_egneration")
def chat_endpoint(list_email: List):
    email_generation(list_email)

    return {"response": "ok"}
