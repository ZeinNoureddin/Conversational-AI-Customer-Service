from fastapi import APIRouter
from app.sessions.store import clear_state, load_state

router = APIRouter()

@router.post("/terminate_session")
async def terminate_session(user_id: str):
    prev = load_state(user_id)
    if prev:
        clear_state(user_id)
        return {"message": "Session terminated successfully"}
    else:
        return {"message": "No active session found for the user"}