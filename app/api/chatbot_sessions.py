from fastapi import APIRouter, Depends
from app.sessions.store import clear_state, load_state
from app.core.models import Users
from app.api.auth import get_current_user

router = APIRouter()

@router.delete("/sessions")
async def terminate_session(current_user: Users = Depends(get_current_user)):
    user_id = str(current_user.user_id)
    clear_state(user_id)
    return {"detail": "Session deleted"}