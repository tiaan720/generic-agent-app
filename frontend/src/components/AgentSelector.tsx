import type React from "react";
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Calculator, PenTool, Bot, Lightbulb, User, Zap, CheckCircle } from "lucide-react";
import { AgentInfo, fetchAgents } from "@/lib/agent-types";

// Icon mapping for dynamic icon display
const iconMap: Record<string, React.ComponentType<any>> = {
  Calculator,
  PenTool,
  Bot,
  Lightbulb,
  User,
  Zap,
  CheckCircle,
};

interface AgentSelectorProps {
  onAgentSelect: (agent: AgentInfo) => void;
  isLoading?: boolean;
}

export function AgentSelector({ onAgentSelect, isLoading = false }: AgentSelectorProps) {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loadingAgents, setLoadingAgents] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAgents = async () => {
      try {
        setLoadingAgents(true);
        const response = await fetchAgents();
        setAgents(response.agents);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load agents');
      } finally {
        setLoadingAgents(false);
      }
    };

    loadAgents();
  }, []);

  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName] || Bot;
    return <IconComponent className="h-6 w-6" />;
  };

  if (loadingAgents) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-neutral-400" />
        <span className="ml-2 text-neutral-400">Loading agents...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-400 p-8">
        <p>Error loading agents: {error}</p>
        <Button 
          variant="outline" 
          onClick={() => window.location.reload()}
          className="mt-4"
        >
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-neutral-100 mb-2">Choose Your Assistant</h2>
        <p className="text-neutral-400">Select an AI assistant to help with your task</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {agents.map((agent) => (
          <Card 
            key={agent.id} 
            className="bg-neutral-800 border-neutral-700 hover:border-neutral-600 transition-colors cursor-pointer"
            onClick={() => onAgentSelect(agent)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div 
                  className="p-2 rounded-lg"
                  style={{ backgroundColor: `${agent.primary_color}20`, color: agent.primary_color }}
                >
                  {getIcon(agent.icon)}
                </div>
                <div>
                  <CardTitle className="text-lg text-neutral-100">{agent.name}</CardTitle>
                  <Badge variant="secondary" className="text-xs">
                    {agent.category}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="pt-0">
              <CardDescription className="text-neutral-400 mb-4 min-h-[3rem]">
                {agent.description}
              </CardDescription>
              
              <div className="space-y-3">
                <div>
                  <h4 className="text-sm font-medium text-neutral-300 mb-2">Available Tools:</h4>
                  <div className="flex flex-wrap gap-1">
                    {agent.tools.map((tool) => (
                      <Badge key={tool.name} variant="outline" className="text-xs">
                        {tool.name.replace('_', ' ')}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-neutral-300 mb-2">Example queries:</h4>
                  <div className="text-xs text-neutral-500">
                    {agent.example_queries.slice(0, 2).map((query, index) => (
                      <div key={index} className="truncate">
                        • {query}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <Button 
                className="w-full mt-4" 
                style={{ backgroundColor: agent.primary_color }}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Loading...
                  </>
                ) : (
                  `Start with ${agent.name}`
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
