# async def run_graph(user_id: str, message: str) -> str:
#     # Placeholder response for now
#     return f"(debug) Received from {user_id}: {message}"
# 6. app/langgraph_agent/graph.py
# ---------------------
from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

class GraphState(TypedDict):
    user_id: str
    latest_user_message: str
    intent: str

# Gemini model setup (Gemini 1.5 Flash)
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)

from app.langgraph_agent.prompts import SYSTEM_PROMPT

async def extract_intent_node(state: GraphState) -> GraphState:
    message = state["latest_user_message"]
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {message}\nIntent:"

    response = await model.ainvoke(prompt)
    intent = response.content.strip().lower()
    state["intent"] = intent
    return state

# Define the graph structure
def build_graph() -> Runnable:
    builder = StateGraph(GraphState)
    builder.add_node("extract_intent", extract_intent_node)
    builder.set_entry_point("extract_intent")
    return builder.compile()

# Entry point for FastAPI
async def run_graph(user_id: str, message: str) -> dict:
    graph = build_graph()
    result = await graph.ainvoke({
        "user_id": user_id,
        "latest_user_message": message,
        "intent": None
    })
    return {"intent": result["intent"]}
