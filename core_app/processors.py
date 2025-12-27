import json
from typing import List, Dict
from django.db import transaction
from . import serializers, models
from helper.classes import LLMModel
from langchain_core.messages import AIMessage
from workflows.create_debate_agents.flows import debate_agents_creation_graph
from workflows.debate.flows import debate_graph
from .utils import parse_agents, AgentResponseStreamingParser
from config import context_storage

class DebateCreateProcessor:
    """
    Handles creation of a debate, including generating the debate title,
    initializing agents, expanding them, and saving everything to the database.
    """

    DEBATE_TITLE_PROMPT = """
        Generate a single, creative 3-word debate title based strictly on the provided User Topic.
        ### Rules:
        Output ONLY the title
        Title must be exactly 3 words
        No explanations, no greetings, no punctuation, nothing extra
        No quotes around the title
        ### User Topic
        {USER_TOPIC}
    """

    def __init__(self, request, project_id: str):
        self.request = request
        self.project_id = project_id


    def _send_event(self, event: str, data: dict):
        """
        Utility to send server-sent events (SSE) data format.
        """
        # take only str and int from data
        filtered_data = {k: v for k, v in data.items() if isinstance(v, (str, int, list, dict))}
        return f"event: {event}\ndata: {json.dumps(filtered_data)}\n\n"

    def _invoke_llm(self, prompt: str) -> str:
        """
        Centralized LLM call for generating responses.
        """
        llm = LLMModel(project_id=self.project_id, debate_id=None, agent_id=None)
        response: AIMessage = llm.invoke_with_log(prompt)
        return response.content.strip()

    def generate_debate_name(self, topic: str) -> str:
        """
        Generate a creative 3-word debate title based on user topic.
        """
        prompt = self.DEBATE_TITLE_PROMPT.format(USER_TOPIC=topic)
        return self._invoke_llm(prompt)

    def create_debate(self) -> models.Debate:
        """
        Creates the Debate instance with LLM-generated name.
        """
        debate_data = self.request.data.copy()
        debate_data["name"] = self.generate_debate_name(debate_data["topic"])
        debate_data["agents"] = []  # Initialize empty agents list
        serializer = serializers.DebateSerializer(data=debate_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def _process_agents(self, debate: models.Debate, expanded_agents: List[Dict]):
        """
        Save expanded agents and link them to the debate.
        """
        for agent_data in expanded_agents:
            agent_data["project"] = self.project_id
            serializer = serializers.AgentSerializer(data=agent_data)
            serializer.is_valid(raise_exception=True)
            agent: models.Agent = serializer.save(project_id=self.project_id)
            debate.agents.add(agent)
            yield self._send_event(
                "agent_saved",
                {"agent_id": str(agent.id), "agent_name": agent.name}
            )
        debate.save()

    def process(self):
        """
        Complete workflow:
        1. Create debate
        2. Stream agent creation & expansion
        3. Save expanded agents
        4. Return list of expanded agents
        """

        with transaction.atomic():
            debate = self.create_debate()
            yield self._send_event("debate_created", {"debate_id": str(debate.id)})

            # Initial state for agent creation workflow
            state = {
                "model": LLMModel(project_id=self.project_id, debate_id=debate.id, agent_id=None),
                "user_topic": debate.topic,
                "initial_agents_prompt": "",
                "agent_expansion_prompt": "",
                "initial_agents": [],
                "current_initial_agent_index": 0,
                "expanded_agents": [],
                "_verbose": True
            }

            final_state = None
            for chunk in debate_agents_creation_graph.stream(state, stream_mode="updates"):
                node, state = list(chunk.items())[0]
                yield self._send_event(node.replace(" ", "_").lower(), state)
                final_state = state

            expanded_agents = parse_agents("\n".join(final_state["expanded_agents"]))
            yield from self._process_agents(debate, expanded_agents)
            yield self._send_event("debate_setup_complete", {"debate_id": str(debate.id)})


class DebateFlowProcessor:
    """Orchestrates debate execution, agent streaming, and UI event emission."""

    def __init__(self, request, debate: models.Debate):
        self.request = request
        self.debate = debate
        self.project_id = debate.project.id
        self.last_node = None

    # ------------------------------------------------------------------
    # SSE Utilities
    # ------------------------------------------------------------------

    def _send_event(self, event: str, data: dict):
        """Formats data as a Server-Sent Event."""
        
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    def _send_status(self, message: str):
        """Sends a UI status update."""
        
        return self._send_event("status", {"message": message})

    # ------------------------------------------------------------------
    # System Agents
    # ------------------------------------------------------------------

    def get_or_create_system_agents(self) -> Dict[str, models.Agent]:
        """Ensures all required system agents exist."""
        
        definitions = [
            ("Summary Agent", "Summarizer", "Summarize debate progress."),
            ("Super Agent", "Moderator", "Control debate flow."),
            ("Final Decision Agent", "Decision Maker", "Produce final decision.")
        ]

        agents = {}
        for name, role, goal in definitions:
            agent, _ = models.Agent.objects.get_or_create(
                name=name,
                org_id = context_storage.get_current_org().id,
                project_id=self.project_id,
                is_system_agent=True,
                defaults={
                    "role": role,
                    "goal": goal,
                    "domain_expertise": role,
                    "debate_style": "Neutral",
                    "backstory": "",
                    "category": "system_agent",
                }
            )
            agents[name.replace(" ", "_").lower()] = agent

        return agents

    # ------------------------------------------------------------------
    # Streaming Helpers
    # ------------------------------------------------------------------

    def _stream_agent_response(self, content: str, parser: AgentResponseStreamingParser):
        """Streams agent response tokens to the UI."""
        
        event_data = parser.process_token(content)
        event_type = event_data.get("event")

        if event_type == "agent_start":
            yield self._send_event(
                "agent_response_start",
                {
                    "agent": event_data["agent"],
                    "emotion": event_data["emotion"],
                }
            )

        if event_type == "token":
            yield self._send_event(
                "agent_response_token",
                {"content": event_data["content"]}
            )

        if event_type == "agent_end":
            yield self._send_event("agent_response_end", {})

        return None

    # ------------------------------------------------------------------
    # Main Processor
    # ------------------------------------------------------------------

    def process(self):
        """Runs the debate workflow and streams events."""
        
        yield self._send_event(
            "debate_started_or_continued",
            {"debate_id": str(self.debate.id)}
        )

        system_agents = self.get_or_create_system_agents()

        state = {
            "model": LLMModel(
                project_id=self.project_id,
                debate_id=self.debate.id,
            ),
            "debate": self.debate,
            "summary_agent": system_agents["summary_agent"],
            "super_agent": system_agents["super_agent"],
            "final_decision_agent": system_agents["final_decision_agent"],
            "memory": "",
            "super_agent_response": dict(),
            "org" : context_storage.get_current_org(),
            "_verbose": True,
        }

        parser = AgentResponseStreamingParser()

        for message, meta in debate_graph.stream(
            state, stream_mode="messages"
        ):
            message: AIMessage
            node = meta.get("langgraph_node")
            content = message.content or ""
            response_metadata = message.response_metadata or {}

            # ----------------------------------------------------------
            # Node: Super Agent Decision
            # ----------------------------------------------------------
            if node == "Super Agent Decision":
                if self.last_node != node:
                    yield self._send_status("Super Agent is evaluating the debate...")
                    self.last_node = node

                if "finish_reason" in response_metadata:
                    yield self._send_status("Super Agent decision complete.")

            # ----------------------------------------------------------
            # Node: Collect Speak Intentions
            # ----------------------------------------------------------
            elif node == "Collect Speak Intentions":
                if self.last_node != node:
                    yield self._send_status("Agents are declaring speak intentions...")
                    self.last_node = node

                if "finish_reason" in response_metadata:
                    yield self._send_status("Speak intentions collected.")

            # ----------------------------------------------------------
            # Node: Execute Debate Turn
            # ----------------------------------------------------------
            elif node == "Execute Debate Turn":
                if content:
                    event = self._stream_agent_response(content, parser)
                    if event:
                        yield event

                if "finish_reason" in response_metadata:
                    parser = AgentResponseStreamingParser()

            # ----------------------------------------------------------
            # Node: Generate Final Decision
            # ----------------------------------------------------------
            elif node == "Generate Final Decision":
                if self.last_node != node:
                    yield self._send_status(
                        "Final Decision Agent is generating the conclusion..."
                    )
                    self.last_node = node

                if content:
                    event = self._stream_agent_response(content, parser)
                    if event:
                        yield event

                if "finish_reason" in response_metadata:
                    parser = AgentResponseStreamingParser()
                    yield self._send_status("Final decision generated.")