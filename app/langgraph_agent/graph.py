# 6. app/langgraph_agent/graph.py
# ---------------------
from typing import TypedDict, Optional, Dict
from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from dotenv import load_dotenv

load_dotenv()

class GraphState(TypedDict):
    user_id: str
    latest_user_message: str
    intent: Optional[str]
    parameters: Dict[str, str]
    missing_params: Optional[list[str]]
    follow_up_prompt: Optional[str]

# Gemini model setup (Gemini 1.5 Flash)
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)

from app.langgraph_agent.prompts import SYSTEM_PROMPT

INTENT_REQUIRED_PARAMS = {
    "get_order": ["order_id"],
    "update_profile": ["email"],
    "search_products": ["query"],
    "get_my_orders": ["order_id"]
}

async def extract_intent_node(state: GraphState) -> GraphState:
    message = state["latest_user_message"]
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {message}\nIntent:"

    response = await model.ainvoke(prompt)
    intent = response.content.strip().lower()
    state["intent"] = intent
    return state

async def extract_parameters_node(state: GraphState) -> GraphState:
    intent = state["intent"]
    message = state["latest_user_message"]
    required = INTENT_REQUIRED_PARAMS.get(intent, [])

    param_prompt = (
        f"You are an AI extracting parameters from a message for the '{intent}' intent.\n"
        f"Required parameters: {', '.join(required)}\n"
        f"User: {message}\n"
        f"Respond with a JSON object with keys {required}"
    )
    response = await model.ainvoke(param_prompt)

    try:
        # extracted = eval(response.content)  # in production use `json.loads` with stricter formatting
        extracted = json.loads(response.content)
    except:
        extracted = {}

    state["parameters"] = extracted
    state["missing_params"] = [
        key for key in required 
        if key not in extracted or not extracted[key]
    ]
    print("HEREE extraction")
    return state

async def ask_for_missing_node(state: GraphState) -> GraphState:
    print("HEREEE missing")
    missing = state["missing_params"]
    prompt = (
        f"You are assisting a user who wants to '{state['intent']}'.\n"
        f"However, you're missing the following parameters: {', '.join(missing)}.\n"
        f"Kindly ask the user to provide them one by one in a polite, conversational tone."
    )
    response = await model.ainvoke(prompt)
    print(f"Response from Gemini: {response.content.strip()}")
    state["follow_up_prompt"] = response.content.strip()
    return state


# Define the graph structure
def build_graph() -> Runnable:
    builder = StateGraph(GraphState)
    builder.add_node("extract_intent", extract_intent_node)
    builder.add_node("extract_parameters", extract_parameters_node)
    builder.add_node("ask_for_missing", ask_for_missing_node)
    builder.add_node("end", lambda x: x)

    builder.set_entry_point("extract_intent")
    builder.add_edge("extract_intent", "extract_parameters")

    builder.add_conditional_edges(
        "extract_parameters",
        lambda s: "ask_for_missing" if s["missing_params"] else END
    )

    builder.add_edge("ask_for_missing", END)

    return builder.compile()

# Entry point for FastAPI
async def run_graph(user_id: str, message: str) -> dict:
    graph = build_graph()
    result = await graph.ainvoke({
        "user_id": user_id,
        "latest_user_message": message,
        "intent": None,
        "parameters": {},
        "missing_params": [],
        "follow_up_prompt": None
    })

    return {
        "intent": result["intent"],
        "parameters": result["parameters"],
        "missing_params": result.get("missing_params", []),
        "follow_up_prompt": result.get("follow_up_prompt")
    }
