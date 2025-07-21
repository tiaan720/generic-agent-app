# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
import pathlib
load_dotenv(dotenv_path=pathlib.Path(__file__).parent.parent / ".env")

# Embedded Agent Registry (to avoid import issues)
class ToolInfo:
    def __init__(self, name: str, description: str, parameters: Dict[str, Any], icon: str):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.icon = icon

class AgentInfo:
    def __init__(self, id: str, name: str, description: str, category: str, tools: List[ToolInfo], 
                 primary_color: str, icon: str, example_queries: List[str]):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.tools = tools
        self.primary_color = primary_color
        self.icon = icon
        self.example_queries = example_queries

# Agent Registry
AGENT_REGISTRY: Dict[str, AgentInfo] = {
    "agent": AgentInfo(
        id="agent",
        name="Math Assistant",
        description="Performs calculations and solves math problems.",
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
        example_queries=[]
    ),
    "creative-agent": AgentInfo(
        id="creative-agent",
        name="Creative Writing Assistant", 
        description="Helps develop stories, characters, and plots.",
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
        example_queries=[]
    )
}

def get_agent_info(agent_id: str) -> Optional[AgentInfo]:
    """Get information about a specific agent."""
    return AGENT_REGISTRY.get(agent_id)

def get_all_agents() -> List[AgentInfo]:
    """Get information about all available agents."""
    return list(AGENT_REGISTRY.values())

# Define the FastAPI app
app = FastAPI()

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes for agent metadata
@app.get("/api/agents")
async def list_agents():
    """Get information about all available agents."""
    agents = get_all_agents()
    return {
        "agents": [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "category": agent.category,
                "primary_color": agent.primary_color,
                "icon": agent.icon,
                "example_queries": agent.example_queries,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                        "icon": tool.icon
                    }
                    for tool in agent.tools
                ]
            }
            for agent in agents
        ]
    }

@app.get("/api/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent."""
    agent = get_agent_info(agent_id)
    if not agent:
        return {"error": "Agent not found"}, 404
    
    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "category": agent.category,
        "primary_color": agent.primary_color,
        "icon": agent.icon,
        "example_queries": agent.example_queries,
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "icon": tool.icon
            }
            for tool in agent.tools
        ]
    }


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
