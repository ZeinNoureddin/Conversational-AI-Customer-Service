# app/state_store.py
from typing import Optional
from app.langgraph_agent.graph import GraphState

# simple in-memory map: user_id → last GraphState
_SESSION_STORE: dict[str, GraphState] = {}

def load_state(user_id: str) -> Optional[GraphState]:
    state = _SESSION_STORE.get(user_id)
    print(f"LOAD_STATE: user_id={user_id}, state={state}")
    return state

def save_state(user_id: str, state: GraphState) -> None:
    _SESSION_STORE[user_id] = state
    print(f"SAVE_STATE: user_id={user_id}, state={state}")

def clear_state(user_id: str) -> None:
    if user_id in _SESSION_STORE:
        print(f"CLEAR_STATE: Clearing state for user_id={user_id}")
        del _SESSION_STORE[user_id]
    else:
        print(f"CLEAR_STATE: No state found for user_id={user_id}")
