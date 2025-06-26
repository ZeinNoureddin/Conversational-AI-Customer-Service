from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.langgraph_agent.graph import run_graph

router = APIRouter()

class Message(BaseModel):
    user_id: str
    message: str

@router.post("/message")
async def handle_message(msg: Message):
    response = await run_graph(user_id=msg.user_id, message=msg.message)
    return {"response": response}