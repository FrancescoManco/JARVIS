from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from Jarvis.orchestrator.orchestrator import MultiAgentOrchestrator

router = APIRouter()
orchestrator = MultiAgentOrchestrator()

class UserInput(BaseModel):
    message: str

@router.post("/chat")
def chat_endpoint(message : str):
    response = orchestrator.invoke(message)
    return {"response": response}
