# chat_ui.py
import gradio as gr
import asyncio
from app.langgraph_agent.graph import run_graph

# Wrapper to run async call in sync Gradio UI
def chatbot_wrapper(user_message, user_id="demo-user"):
    result = asyncio.run(run_graph(user_id=user_id, message=user_message))
    if result["follow_up_prompt"]:
        return result["follow_up_prompt"]
    return f"Intent: {result['intent']}\nParameters: {result['parameters']}"

# Launch Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 AI Chat Interface")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Message", placeholder="Ask me anything about your orders, profile, etc.")
        
    def respond(user_input, history):
        response = chatbot_wrapper(user_input)
        history = history + [[user_input, response]]
        return history, ""

    msg.submit(respond, [msg, chatbot], [chatbot, msg])

demo.launch()
