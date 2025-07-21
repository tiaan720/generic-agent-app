import os
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from agent.state import OverallState

load_dotenv()

if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is not set")


# Define the plus calculator tool
@tool
def plus_calculator(a: int, b: int) -> int:
    """Add two numbers together.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        The sum of a and b
    """
    return a + b


# Define the multiply calculator tool
@tool
def multiply_calculator(a: int, b: int) -> int:
    """Multiply two numbers together.
    
    Args:
        a: First number to multiply
        b: Second number to multiply
        
    Returns:
        The product of a and b
    """
    return a * b


def dummy_agent_node(state: OverallState, config: RunnableConfig) -> OverallState:
    """Simple dummy agent node that uses a ReAct agent with plus_calculator tool.
    
    Args:
        state: Current graph state containing messages
        config: Configuration for the runnable
        
    Returns:
        Updated state with the agent's response
    """
    # Get the user's message
    user_message = state["messages"][-1].content if state["messages"] else "What is 1 + 1?"
    
    # Create the ReAct agent
    system_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful mathematical assistant. Your task is simple:

1. When a user asks you to add two numbers, use the plus_calculator tool
2. When a user asks you to multiply two numbers, use the multiply_calculator tool
3. Use the appropriate tool based on the mathematical operation requested
4. Call the tool with the two numbers from the user's question
5. Return the result to the user
6. Do NOT call multiple tools for the same operation
7. Do NOT overthink the problem

Examples:
- For "What is 5 + 3?": Call plus_calculator(5, 3)
- For "What is 4 times 6?": Call multiply_calculator(4, 6)
- For "Multiply 7 by 8": Call multiply_calculator(7, 8)

Be direct and concise. One tool call, one answer, done."""),
        ("human", "{messages}"),
    ])

    # Use Gemini model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.0,
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    # Create the ReAct agent
    agent = create_react_agent(
        model=model,
        tools=[plus_calculator, multiply_calculator],
        prompt=system_prompt,
        store=InMemoryStore(),
    )
    
    # Run the agent
    agent_input = {"messages": [("user", user_message)]}
    result = agent.invoke(agent_input, config={"configurable": {"thread_id": "1"}})
    
    # Extract the final response
    final_message = result["messages"][-1]
    if hasattr(final_message, 'content'):
        response_content = final_message.content
    else:
        response_content = str(final_message)
    
    return {
        "messages": [AIMessage(content=response_content)]
    }


# Create our simplified Agent Graph
builder = StateGraph(OverallState)

# Define the single node
builder.add_node("dummy_agent", dummy_agent_node)

# Set the entrypoint and exit
builder.add_edge(START, "dummy_agent")
builder.add_edge("dummy_agent", END)

graph = builder.compile(name="dummy-agent")
