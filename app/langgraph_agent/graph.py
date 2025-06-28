# 6. app/langgraph_agent/graph.py
# ---------------------
from typing import TypedDict, Optional, Dict
from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
from dotenv import load_dotenv
from app.db.functions import (
    get_order,
    update_profile,
    search_products,
    get_my_orders
)

load_dotenv()

class GraphState(TypedDict):
    user_id: str
    latest_user_message: str
    intent: Optional[str]
    parameters: Dict[str, str]
    missing_params: Optional[list[str]]
    LLM_response: Optional[str]
    execution_response: Optional[dict]

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)

from app.langgraph_agent.prompts import SYSTEM_PROMPT

INTENT_REQUIRED_PARAMS = {
    "get_order": ["order_id"],
    "update_profile": ["email"],
    "search_products": ["query"],
    "get_my_orders": ["order_id"],
    "chatting": []
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

    print(f"\nGEMINI RESPONSE: {response.content.strip()}")
    # print(f"\nGEMINI RESPONSE NOT STRIPPED: {response.content}")

    try:
        result = json.loads(raw)
        # print(f"\nParsed result: {result}")
    except json.JSONDecodeError:
        result = {"intent": None, "parameters": {}}
        # print("\nFAILED to parse response, using default empty intent and parameters.")

    state["intent"] = result.get("intent")
    # print(f"\nEXTRACTED INTENT: {state['intent']}")
    state["parameters"] = result.get("parameters", {})
    required = INTENT_REQUIRED_PARAMS.get(state["intent"], [])
    state["missing_params"] = [
        key for key in required 
        if key not in state["parameters"] or not state["parameters"][key]
    ]

    return state

async def ask_for_missing_node(state: GraphState) -> GraphState:
    print("\nHEREEE missing")
    missing = state["missing_params"]
    print(f"\n\nMISSING parameters: {missing}")
    prompt = (
        f"You are assisting a user who wants to '{state['intent']}'.\n"
        f"However, you're missing the following parameters: {', '.join(missing)}.\n"
        f"Kindly ask the user to provide them one by one in a polite, conversational tone."
    )
    response = await model.ainvoke(prompt)
    # print(f"\nResponse from Gemini: {response.content.strip()}")
    state["LLM_response"] = response.content.strip()
    return state

async def execute_intent_node(state: GraphState) -> GraphState:
    intent = state["intent"]
    parameters = state["parameters"]

    if intent == "get_order":
        # Call the function for 'get_order' intent
        state["execution_response"] = get_order(parameters["order_id"])
    elif intent == "update_profile":
        # Call the function for 'update_profile' intent
        state["execution_response"] = update_profile(parameters["email"])
    elif intent == "search_products":
        # Call the function for 'search_products' intent
        state["execution_response"] = search_products(parameters["query"])
    elif intent == "get_my_orders":
        # Call the function for 'get_my_orders' intent
        state["execution_response"] = get_my_orders(parameters["order_id"])
    else:
        state["execution_response"] = {"error": "Unknown intent"}

    print(f"\nRESPONSE when executing intent '{intent}': {state['execution_response']}")
    return state

async def formulate_response_node(state: GraphState) -> GraphState:
    execution_response = state.get("execution_response", {})
    print(f"\nFORMULATING RESPONSE with execution_response: {execution_response}")
    user_message = state.get("latest_user_message", "")
    intent = state.get("intent", "unknown")

    prompt = (
        f"You are an AI assistant formulating a response for the user.\n"
        f"The user requested: '{user_message}'.\n"
        f"The intent identified was: '{intent}'.\n"
        f"The result of the execution is: {execution_response}.\n"
        f"Please provide a polite and concise response to the user summarizing what was executed and the result."
    )

    response = await model.ainvoke(prompt)
    state["LLM_response"] = response.content.strip()

    return state

def build_graph() -> Runnable:
    builder = StateGraph(GraphState)
    builder.add_node("extract_intent_and_parameters", extract_intent_and_parameters_node)
    builder.add_node("ask_for_missing", ask_for_missing_node)
    builder.add_node("execute_intent", execute_intent_node)
    builder.add_node("formulate_response", formulate_response_node)
    builder.add_node("end", lambda x: x)

    builder.set_entry_point("extract_intent_and_parameters")

    builder.add_conditional_edges(
        "extract_intent_and_parameters",
        lambda s: "ask_for_missing" if s["missing_params"] else ("formulate_response" if s["intent"] == "chatting" else "execute_intent")
    )

    builder.add_conditional_edges(
        "ask_for_missing",
        lambda s: END if s["LLM_response"] else "execute_intent"
    )

    builder.add_edge("execute_intent", "formulate_response")
    builder.add_edge("formulate_response", END)

    return builder.compile()

async def run_graph(user_id: str, message: str) -> dict:
    graph = build_graph()
    result = await graph.ainvoke({
        "user_id": user_id,
        "latest_user_message": message,
        "intent": None,
        "parameters": {},
        "missing_params": [],
        "LLM_response": None
    })

    return {
        "intent": result["intent"],
        "parameters": result["parameters"],
        "missing_params": result.get("missing_params", []),
        "LLM_response": result.get("LLM_response")
    }

async def run_graph_with_state(state: GraphState) -> GraphState:
    """Continues the graph from an existing state snapshot."""
    print("\nHERE in run_graph_with_state")
    print(f"\nSTATE before invoking graph: {state}")
    graph = build_graph()
    return await graph.ainvoke(state)