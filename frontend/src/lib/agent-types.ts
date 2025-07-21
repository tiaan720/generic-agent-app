// Agent metadata types for dynamic frontend configuration
export interface ToolInfo {
  name: string;
  description: string;
  parameters: Record<string, string>;
  icon: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  category: string;
  tools: ToolInfo[];
  primary_color: string;
  icon: string;
  example_queries: string[];
}

export interface AgentListResponse {
  agents: AgentInfo[];
}

// Event processing types for dynamic activity timeline
export interface ProcessedEvent {
  title: string;
  data: any;
  icon?: string;
  timestamp?: string;
}

// Generic event processor that works with any agent
export class GenericEventProcessor {
  private agentInfo: AgentInfo;

  constructor(agentInfo: AgentInfo) {
    this.agentInfo = agentInfo;
  }

  processEvent(event: any): ProcessedEvent | null {
    // Handle common event types that work across all agents
    if (event.__start__) {
      return {
        title: `Starting ${this.agentInfo.name}`,
        data: `Initializing ${this.agentInfo.name.toLowerCase()} to process your request`,
        icon: this.agentInfo.icon,
      };
    }

    if (event.__end__) {
      return {
        title: `${this.agentInfo.name} Complete`,
        data: `Successfully processed your request using ${this.agentInfo.name.toLowerCase()}`,
        icon: "CheckCircle",
      };
    }

    // Handle tool calls generically
    for (const tool of this.agentInfo.tools) {
      if (event[tool.name]) {
        return {
          title: `Using ${tool.name.replace('_', ' ')}`,
          data: `${tool.description} - Processing your request`,
          icon: tool.icon,
        };
      }
    }

    // Handle agent node execution generically  
    const agentNodeKey = this.getAgentNodeKey(event);
    if (agentNodeKey && event[agentNodeKey]) {
      return {
        title: `Processing with ${this.agentInfo.name}`,
        data: `Agent is analyzing your request and selecting appropriate tools`,
        icon: this.agentInfo.icon,
      };
    }

    return null;
  }

  private getAgentNodeKey(event: any): string | null {
    // Try to identify the agent node key dynamically
    const possibleKeys = [
      'dummy_agent',
      'creative_agent', 
      'math_agent',
      'agent',
      // Add more patterns as needed
    ];

    for (const key of possibleKeys) {
      if (event[key]) {
        return key;
      }
    }

    // If no known key found, look for any key that's not a system key
    const systemKeys = ['__start__', '__end__', 'messages'];
    const eventKeys = Object.keys(event);
    
    for (const key of eventKeys) {
      if (!systemKeys.includes(key) && !key.startsWith('__')) {
        return key;
      }
    }

    return null;
  }
}

// API functions for fetching agent metadata
export async function fetchAgents(): Promise<AgentListResponse> {
  const apiUrl = import.meta.env.DEV 
    ? "http://localhost:2024" 
    : "http://localhost:8123";
    
  const response = await fetch(`${apiUrl}/api/agents`);
  if (!response.ok) {
    throw new Error('Failed to fetch agents');
  }
  return response.json();
}

export async function fetchAgentInfo(agentId: string): Promise<AgentInfo> {
  const apiUrl = import.meta.env.DEV 
    ? "http://localhost:2024" 
    : "http://localhost:8123";
    
  const response = await fetch(`${apiUrl}/api/agents/${agentId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch agent ${agentId}`);
  }
  return response.json();
}
