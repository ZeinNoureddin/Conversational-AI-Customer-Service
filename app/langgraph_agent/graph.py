# 6. app/langgraph_agent/graph.py
# ---------------------
from typing import TypedDict, Optional, Dict
from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
from dotenv import load_dotenv

load_dotenv()

class GraphState(TypedDict):
    user_id: str
    latest_user_message: str
    intent: Optional[str]
    parameters: Dict[str, str]
    missing_params: Optional[list[str]]
    follow_up_prompt: Optional[str]

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)

from app.langgraph_agent.prompts import SYSTEM_PROMPT

INTENT_REQUIRED_PARAMS = {
    "get_order": ["order_id"],
    "update_profile": ["email"],
    "search_products": ["query"],
    "get_my_orders": ["order_id"]
}

async def extract_intent_and_parameters_node(state: GraphState) -> GraphState:
    message = state["latest_user_message"]
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {message}\nAgain, respond with ONLY a JSON object, no markdown fences, no explanation."    

    response = await model.ainvoke(prompt)

    raw = response.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        raw = match.group(0)

    print(f"GEMINI RESPONSE: {response.content.strip()}")
    # print(f"GEMINI RESPONSE NOT STRIPPED: {response.content}")

    try:
        result = json.loads(raw)
        # print(f"Parsed result: {result}")
    except json.JSONDecodeError:
        result = {"intent": None, "parameters": {}}
        # print("FAILED to parse response, using default empty intent and parameters.")

    state["intent"] = result.get("intent")
    # print(f"EXTRACTED INTENT: {state['intent']}")
    state["parameters"] = result.get("parameters", {})
    required = INTENT_REQUIRED_PARAMS.get(state["intent"], [])
    state["missing_params"] = [
        key for key in required 
        if key not in state["parameters"] or not state["parameters"][key]
    ]

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
    # print(f"Response from Gemini: {response.content.strip()}")
    state["follow_up_prompt"] = response.content.strip()
    return state

def build_graph() -> Runnable:
    builder = StateGraph(GraphState)
    builder.add_node("extract_intent_and_parameters", extract_intent_and_parameters_node)
    builder.add_node("ask_for_missing", ask_for_missing_node)
    builder.add_node("end", lambda x: x)

    builder.set_entry_point("extract_intent_and_parameters")

    builder.add_conditional_edges(
        "extract_intent_and_parameters",
        lambda s: "ask_for_missing" if s["missing_params"] else END
    )

    builder.add_edge("ask_for_missing", END)

    return builder.compile()

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

async def run_graph_with_state(state: GraphState) -> GraphState:
    """Continues the graph from an existing state snapshot."""
    print("HERE in run_graph_with_state")
    print(f"STATE before invoking graph: {state}")
    graph = build_graph()
    return await graph.ainvoke(state)