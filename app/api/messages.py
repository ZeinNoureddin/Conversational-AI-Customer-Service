from fastapi import APIRouter
from pydantic import BaseModel
from app.sessions.store import load_state, save_state
from app.langgraph_agent.graph import run_graph_with_state, run_graph
from app.db.functions import save_conversation

router = APIRouter()

class Message(BaseModel):
    user_id: str
    message: str

@router.post("/message")
async def handle_message(msg: Message):
    save_conversation(msg.user_id, msg.message, direction="user")

    prev = load_state(msg.user_id)

    if prev:
        initial_state = {
            "user_id": msg.user_id,
            "latest_user_message": msg.message,
            "intent": prev["intent"],
            "parameters": prev["parameters"],
            "missing_params": prev["missing_params"],
            "follow_up_prompt": None
        }
        result = await run_graph_with_state(initial_state)
    else:
        result = await run_graph(user_id=msg.user_id, message=msg.message)

    agent_msg = result.get("follow_up_prompt") or "All set!"
    print(f"AGENT response: {agent_msg}")

    save_conversation(msg.user_id, agent_msg, direction="agent")

    save_state(msg.user_id, result)

    return {"response": result}