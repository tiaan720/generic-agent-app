import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";
import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { Button } from "@/components/ui/button";
import { AgentInfo, GenericEventProcessor } from "@/lib/agent-types";

export default function App() {
  const [selectedAgent, setSelectedAgent] = useState<AgentInfo | null>(null);
  const [eventProcessor, setEventProcessor] = useState<GenericEventProcessor | null>(null);
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<
    ProcessedEvent[]
  >([]);
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({});
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const hasFinalizeEventOccurredRef = useRef(false);
  const [error, setError] = useState<string | null>(null);
  
  const thread = useStream<{
    messages: Message[];
  }>({
    apiUrl: import.meta.env.DEV
      ? "http://localhost:2024"
      : "http://localhost:8123",
    assistantId: selectedAgent?.id || "agent", // Dynamic agent selection
    messagesKey: "messages",
    onUpdateEvent: (event: any) => {
      if (!eventProcessor) return;
      
      const processedEvent = eventProcessor.processEvent(event);
      
      if (processedEvent) {
        setProcessedEventsTimeline((prevEvents) => [
          ...prevEvents,
          processedEvent,
        ]);
        
        // Check for finalization events
        if (processedEvent.title.toLowerCase().includes("complete") || 
            event.__end__) {
          hasFinalizeEventOccurredRef.current = true;
        }
      }
    },
    onError: (error: any) => {
      setError(error.message);
    },
  });

  // Initialize event processor when agent is selected
  useEffect(() => {
    if (selectedAgent) {
      setEventProcessor(new GenericEventProcessor(selectedAgent));
    }
  }, [selectedAgent]);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [thread.messages]);

  useEffect(() => {
    if (
      !thread.isLoading &&
      thread.messages.length > 0
    ) {
      const lastMessage = thread.messages[thread.messages.length - 1];
      if (lastMessage && lastMessage.type === "ai" && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }));
      }
      hasFinalizeEventOccurredRef.current = false;
    }
  }, [thread.messages, thread.isLoading, processedEventsTimeline]);

  const handleSubmit = useCallback(
    (submittedInputValue: string, _effort: string, _model: string, agent: AgentInfo) => {
      if (!submittedInputValue.trim()) return;
      
      // Update selected agent if it changed
      if (!selectedAgent || selectedAgent.id !== agent.id) {
        setSelectedAgent(agent);
      }
      
      setProcessedEventsTimeline([]);
      hasFinalizeEventOccurredRef.current = false;

      // Add an initial processing event using the selected agent's info
      setProcessedEventsTimeline([
        {
          title: `Starting ${agent.name}`,
          data: `Analyzing query: "${submittedInputValue}" - ${agent.description.toLowerCase()}`,
          icon: agent.icon,
        },
      ]);

      const newMessages: Message[] = [
        ...(thread.messages || []),
        {
          type: "human",
          content: submittedInputValue,
          id: Date.now().toString(),
        },
      ];
      
      // Submit to the selected agent
      thread.submit({
        messages: newMessages,
      });
    },
    [thread, selectedAgent]
  );

  const handleCancel = useCallback(() => {
    thread.stop();
    window.location.reload();
  }, [thread]);

  const handleAgentChange = useCallback((agent: AgentInfo) => {
    setSelectedAgent(agent);
    setProcessedEventsTimeline([]);
    setHistoricalActivities({});
    setError(null);
  }, []);

  return (
    <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
      <main className="h-full w-full max-w-4xl mx-auto">
        {thread.messages.length === 0 ? (
          <WelcomeScreen
            handleSubmit={handleSubmit}
            isLoading={thread.isLoading}
            onCancel={handleCancel}
            selectedAgent={selectedAgent}
            onAgentChange={handleAgentChange}
          />
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="flex flex-col items-center justify-center gap-4">
              <h1 className="text-2xl text-red-400 font-bold">Error</h1>
              <p className="text-red-400">{JSON.stringify(error)}</p>
              <Button
                variant="destructive"
                onClick={() => window.location.reload()}
              >
                Retry
              </Button>
            </div>
          </div>
        ) : (
          <ChatMessagesView
            messages={thread.messages}
            isLoading={thread.isLoading}
            scrollAreaRef={scrollAreaRef}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            liveActivityEvents={processedEventsTimeline}
            historicalActivities={historicalActivities}
            agentName={selectedAgent?.name || "Assistant"}
            agentColor={selectedAgent?.primary_color || "#3b82f6"}
            selectedAgent={selectedAgent}
            onAgentChange={handleAgentChange}
          />
        )}
      </main>
    </div>
  );
}
