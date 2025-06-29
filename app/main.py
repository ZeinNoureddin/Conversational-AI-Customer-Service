from fastapi import FastAPI
from app.api.messages import router as messages_router
from app.api.chatbot_sessions import router as sessions_router
from app.api.auth import router as auth_router

app = FastAPI()
app.include_router(messages_router)
app.include_router(sessions_router)
app.include_router(auth_router)  