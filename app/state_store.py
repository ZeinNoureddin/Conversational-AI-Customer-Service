# app/state_store.py
from typing import Optional
from app.langgraph_agent.graph import GraphState

# simple in-memory map: user_id → last GraphState
_SESSION_STORE: dict[str, GraphState] = {}

def load_state(user_id: str) -> Optional[GraphState]:
    return _SESSION_STORE.get(user_id)

def save_state(user_id: str, state: GraphState) -> None:
    _SESSION_STORE[user_id] = state

def clear_state(user_id: str) -> None:
    if user_id in _SESSION_STORE:
        del _SESSION_STORE[user_id]
