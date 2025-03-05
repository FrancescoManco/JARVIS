from fastapi import APIRouter


from Jarvis.api.endpoints import email_generation, chat
from Jarvis.api.endpoints import auth_gmail

api_router = APIRouter()

api_router.include_router(email_generation.router, prefix="/email", tags=['email'])
api_router.include_router(auth_gmail.router, prefix="/auth_gmail", tags=['email'])
api_router.include_router(chat.router, prefix="", tags=['chat'])
