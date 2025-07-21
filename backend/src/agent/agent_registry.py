"""
Agent Registry: Central configuration for all available agents.
This module provides metadata about each agent that can be used by the frontend
to dynamically configure UI elements and provide appropriate context.
"""

from typing import Dict, List, Any, Optional
try:
    from dataclasses import dataclass
except ImportError:
    # Fallback for older Python versions
    class dataclass:
        def __init__(self, cls):
            return cls

@dataclass
class ToolInfo:
    """Information about a tool that an agent can use."""
    name: str
    description: str
    parameters: Dict[str, Any]
    icon: str  # Icon name for frontend display

@dataclass  
class AgentInfo:
    """Complete information about an agent."""
    id: str
    name: str
    description: str
    category: str
    tools: List[ToolInfo]
    primary_color: str  # For theming
    icon: str  # Icon name for frontend display
    example_queries: List[str]

# Agent Registry
AGENT_REGISTRY: Dict[str, AgentInfo] = {
    "agent": AgentInfo(
        id="agent",
        name="Math Assistant",
        description="A helpful mathematical assistant that can perform calculations and solve math problems.",
        category="Mathematics",
        tools=[
            ToolInfo(
                name="plus_calculator",
                description="Add two numbers together",
                parameters={"a": "int", "b": "int"},
                icon="Calculator"
            ),
            ToolInfo(
                name="multiply_calculator", 
                description="Multiply two numbers together",
                parameters={"a": "int", "b": "int"},
                icon="Calculator"
            )
        ],
        primary_color="#3b82f6",  # Blue
        icon="Calculator",
        example_queries=[
            "What is 15 + 27?",
            "Calculate 8 times 9",
            "Add 125 and 378",
            "What's 12 * 15?"
        ]
    ),
    "creative-agent": AgentInfo(
        id="creative-agent",
        name="Creative Writing Assistant", 
        description="An inspiring creative writing assistant that helps develop compelling stories, characters, and plots.",
        category="Creative Writing",
        tools=[
            ToolInfo(
                name="generate_story_idea",
                description="Generate creative story ideas based on genre and theme",
                parameters={"genre": "str", "theme": "str"},
                icon="Lightbulb"
            ),
            ToolInfo(
                name="create_character_profile",
                description="Create detailed character profiles for stories",
                parameters={"name": "str", "role": "str", "personality_trait": "str"},
                icon="User"
            ),
            ToolInfo(
                name="suggest_plot_twist",
                description="Suggest creative plot twists for stories",
                parameters={"current_situation": "str", "character_involved": "str"},
                icon="Zap"
            )
        ],
        primary_color="#8b5cf6",  # Purple  
        icon="PenTool",
        example_queries=[
            "Help me create a science fiction story about friendship",
            "I need a villain character for my mystery novel",
            "Suggest a plot twist for my fantasy adventure",
            "Create a character profile for a brave knight"
        ]
    )
}

def get_agent_info(agent_id: str) -> Optional[AgentInfo]:
    """Get information about a specific agent."""
    return AGENT_REGISTRY.get(agent_id)

def get_all_agents() -> List[AgentInfo]:
    """Get information about all available agents."""
    return list(AGENT_REGISTRY.values())

def get_agents_by_category(category: str) -> List[AgentInfo]:
    """Get all agents in a specific category."""
    return [agent for agent in AGENT_REGISTRY.values() if agent.category == category]
