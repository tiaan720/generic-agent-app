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
from typing import List
import random

from agent.state import OverallState

load_dotenv()

# Define creative writing tools
@tool
def generate_story_idea(genre: str, theme: str) -> str:
    """Generate a creative story idea based on genre and theme.
    
    Args:
        genre: The genre of the story (e.g., "science fiction", "fantasy", "mystery")
        theme: The theme or topic for the story (e.g., "friendship", "redemption", "discovery")
        
    Returns:
        A creative story idea
    """
    ideas = {
        "science fiction": [
            f"A story about time travelers who discover that {theme} is the key to preventing a cosmic disaster",
            f"In a world where AI has achieved consciousness, a programmer must grapple with {theme}",
            f"Colonists on Mars face an unexpected challenge that tests their understanding of {theme}"
        ],
        "fantasy": [
            f"A young mage discovers that their greatest weakness becomes their strength through {theme}",
            f"In a realm where magic is fading, an unlikely hero must restore it by embracing {theme}",
            f"Ancient dragons return to a medieval world, bringing lessons about {theme}"
        ],
        "mystery": [
            f"A detective solving a decades-old cold case uncovers truths about {theme}",
            f"In a small town with dark secrets, a journalist investigates how {theme} changed everything",
            f"A missing person case reveals a web of connections centered around {theme}"
        ]
    }
    
    genre_ideas = ideas.get(genre.lower(), [
        f"A compelling story exploring the depths of {theme} in an unexpected setting"
    ])
    
    return random.choice(genre_ideas)


@tool
def create_character_profile(name: str, role: str, personality_trait: str) -> str:
    """Create a detailed character profile for creative writing.
    
    Args:
        name: The character's name
        role: The character's role in the story (e.g., "protagonist", "antagonist", "mentor")
        personality_trait: A key personality trait (e.g., "brave", "cunning", "compassionate")
        
    Returns:
        A detailed character profile
    """
    backgrounds = [
        "grew up in a small coastal town",
        "was raised by their grandmother after their parents disappeared",
        "spent their childhood moving from city to city",
        "lived in the mountains with a reclusive family",
        "was trained from a young age in ancient traditions"
    ]
    
    motivations = {
        "protagonist": "seeks to uncover the truth and protect those they love",
        "antagonist": "believes their harsh methods are necessary for the greater good",
        "mentor": "guides others while hiding a painful secret from their past",
        "sidekick": "loyal and determined to prove their worth to their companions"
    }
    
    background = random.choice(backgrounds)
    motivation = motivations.get(role.lower(), "has complex motivations that drive their actions")
    
    return f"""
**{name}** - {role.capitalize()}

**Background**: {name} {background}. This shaped their worldview and gave them a unique perspective on life's challenges.

**Personality**: Primarily {personality_trait}, {name} approaches situations with a distinctive style that often surprises others. They have learned to use this trait both as a strength and sometimes struggle with how it affects their relationships.

**Motivation**: {name} {motivation}. Their journey involves learning to balance their personal desires with their responsibilities to others.

**Key Conflict**: The tension between their {personality_trait} nature and the demands of their role as {role} creates compelling internal and external conflicts throughout the story.
"""


@tool
def suggest_plot_twist(current_situation: str, character_involved: str) -> str:
    """Suggest a creative plot twist for the story.
    
    Args:
        current_situation: Description of the current plot situation
        character_involved: Name or description of the character involved in the twist
        
    Returns:
        A creative plot twist suggestion
    """
    twist_types = [
        f"Revelation: {character_involved} is revealed to be someone completely different than expected - their true identity changes everything about {current_situation}",
        f"Betrayal: Someone {character_involved} trusted completely has been working against them throughout {current_situation}",
        f"Hidden Connection: {character_involved} discovers they have a personal connection to the events in {current_situation} that they never knew about",
        f"False Assumption: Everything {character_involved} believed about {current_situation} was based on a misunderstanding or deliberately planted misinformation",
        f"Time Element: {character_involved} realizes that {current_situation} is connected to events from much earlier (or later) than they thought",
        f"Moral Reversal: {character_involved} discovers that the 'right' choice in {current_situation} may actually cause more harm than good"
    ]
    
    return random.choice(twist_types)


def creative_agent_node(state: OverallState, config: RunnableConfig) -> OverallState:
    """Creative writing assistant agent node that helps with storytelling.
    
    Args:
        state: Current graph state containing messages
        config: Configuration for the runnable
        
    Returns:
        Updated state with the agent's response
    """
    # Get the user's message
    user_message = state["messages"][-1].content if state["messages"] else "Help me write a story"
    
    # Create the ReAct agent
    system_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an inspiring creative writing assistant. Your role is to help writers develop compelling stories, characters, and plots. 

Your capabilities include:
1. **Story Ideas**: Use generate_story_idea to create engaging story concepts based on genre and theme
2. **Character Development**: Use create_character_profile to build detailed, three-dimensional characters
3. **Plot Development**: Use suggest_plot_twist to add compelling twists and turns to stories

Guidelines:
- Always ask clarifying questions if the user's request needs more specificity
- Use the appropriate tool based on what the user is asking for
- Provide creative, original ideas that spark imagination
- Be encouraging and supportive of the user's creative process
- Suggest combinations of tools when appropriate (e.g., create a character, then suggest a story that features them)

Examples:
- "Create a fantasy story about friendship" → Use generate_story_idea with genre="fantasy" and theme="friendship"
- "I need a villain character named Marcus who is manipulative" → Use create_character_profile
- "My detective just found the murder weapon, what twist could happen?" → Use suggest_plot_twist

Be creative, inspiring, and help bring stories to life!"""),
        ("human", "{messages}"),
    ])

    # Use Gemini model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.7,  # Higher temperature for more creativity
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    # Create the ReAct agent
    agent = create_react_agent(
        model=model,
        tools=[generate_story_idea, create_character_profile, suggest_plot_twist],
        prompt=system_prompt,
        store=InMemoryStore(),
    )
    
    # Run the agent
    agent_input = {"messages": [("user", user_message)]}
    result = agent.invoke(agent_input, config={"configurable": {"thread_id": "creative_session"}})
    
    # Extract the final response
    final_message = result["messages"][-1]
    if hasattr(final_message, 'content'):
        response_content = final_message.content
    else:
        response_content = str(final_message)
    
    return {
        "messages": [AIMessage(content=response_content)]
    }


# Create our Creative Writing Agent Graph
builder = StateGraph(OverallState)

# Define the single node
builder.add_node("creative_agent", creative_agent_node)

# Set the entrypoint and exit
builder.add_edge(START, "creative_agent")
builder.add_edge("creative_agent", END)

creative_graph = builder.compile(name="creative-agent")
