import chainlit as cl
import os
from app3 import RESUME_SHORTLISTER

@cl.on_chat_start
async def start():
    # We define actions with a 'payload' dict to satisfy Pydantic V2
    actions = [
        cl.Action(name="select_model", payload={"value": "groq"}, label="Groq (Fast)"),
        cl.Action(name="select_model", payload={"value": "openai"}, label="OpenAI (Detailed)")
    ]

    # Sending buttons as a Message instead of AskAction to ensure they render
    await cl.Message(
        content="Welcome! Select your AI provider and then upload a PDF resume.",
        actions=actions
    ).send()

@cl.action_callback("select_model")
async def on_action(action: cl.Action):
    # This captures the button click
    selection = action.payload.get("value")
    cl.user_session.set("model", selection)
    
    await action.remove() # Removes buttons from UI after clicking
    await cl.Message(content=f"✅ **{selection.upper()}** selected. Drag and drop your PDF here!").send()

@cl.on_message
async def main(message: cl.Message):
    model_choice = cl.user_session.get("model")
    
    if not model_choice:
        await cl.Message(content="⚠️ Please click a model button first.").send()
        return

    if not message.elements:
        await cl.Message(content="⚠️ Please upload a PDF file.").send()
        return

    # Process the file
    file = message.elements[0]
    
    # In newer Chainlit versions, use file.path to get the temporary file location
    if file.path is None:
        await cl.Message(content="❌ Error: File path not found.").send()
        return

    await cl.Message(content=f"🔍 Analyzing `{file.name}`...").send()

    try:
        # We can pass the file.path directly to your class
        shortlister = RESUME_SHORTLISTER(file.path, model_choice)
        content = shortlister.text_extractor()
        chain = shortlister.get_chain()
        
        # Invoke LLM
        response = await chain.ainvoke({"resume_content": content})
        await cl.Message(content=f"### Result:\n{response}").send()
    except Exception as e:
        await cl.Message(content=f"❌ Error during analysis: {str(e)}").send()
