import os
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

dummy_agent_router = APIRouter()

# Minimal plus_calculator tool
def plus_calculator(a: int, b: int) -> int:
    return a + b

def create_dummy_agent():
    system_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful mathematical assistant. Your task is simple:\n\n1. When a user asks you to add two numbers, use the plus_calculator tool EXACTLY ONCE\n2. Call the tool with the two numbers from the user's question\n3. Return the result to the user\n4. Do NOT call the tool multiple times\n5. Do NOT overthink the problem\n\nFor the question 'What is 1 + 1?':\n- Call plus_calculator(1, 1)\n- Report the result\n- STOP\n\nBe direct and concise. One tool call, one answer, done."""),
        ("human", "{messages}"),
    ])

    # Use Gemini model as in current setup
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.0,
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    agent = create_react_agent(
        model=model,
        tools=[{"name": "plus_calculator", "description": "Add two numbers", "func": plus_calculator}],
        prompt=system_prompt,
        store=InMemoryStore(),
    )
    return agent

@dummy_agent_router.post("/api/dummy-agent/stream")
async def stream_dummy_agent(request: Request):
    body = await request.json()
    query = body.get("query", "What is 1 + 1?")
    agent = create_dummy_agent()
    input = {"messages": [("user", query)]}
    config = {"configurable": {"thread_id": "1"}}
    
    def event_stream():
        for chunk in agent.stream(input, config, stream_mode="updates"):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
