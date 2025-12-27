from django.db.models import QuerySet
from langchain_core.messages import AIMessage
from config import context_storage

from core_app.models import DebateMessage, Agent, Debate
from orgs_app.models import Organization
from core_app.serializers import DebateMessageSerializer

from .schemas import DebateState
from .prompts import SUMMARY_AGENT_PROMPT

def create_debate_message(content: str, debate: Debate, agent: Agent, org : Organization) -> DebateMessage:
    data = {
        "org" : org.id,
        "debate" : debate.id,
        "agent" : agent.id,
        "content" : content
    }

    serializer = DebateMessageSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.instance


def build_memory(debate: Debate) -> str:
    summary = debate.summary or ""
    messages = debate.debate_messages()
    return summary + "\n" + messages


def parse_super_agent_response(text: str) -> dict:
    """
    Parse SuperAgent PAS response into a normalized dict.

    Supported TASK values:
    - continue
    - request_speak_intent
    - final_decision
    """

    parsed = {
        "agent": None,
        "task": None,
        "reasoning": None,
        "next_agent": None,
    }

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        lower = line.lower()

        if lower.startswith("agent:"):
            parsed["agent"] = line.split(":", 1)[1].strip()

        elif lower.startswith("task:"):
            parsed["task"] = line.split(":", 1)[1].strip()

        elif lower.startswith("reasoning:"):
            parsed["reasoning"] = line.split(":", 1)[1].strip()

        elif lower.startswith("next agent:"):
            parsed["next_agent"] = line.split(":", 1)[1].strip()

        elif lower == "end":
            break

    # -------------------------
    # NORMALIZATION & SAFETY
    # -------------------------

    if parsed["task"]:
        parsed["task"] = parsed["task"].lower()

    if parsed["next_agent"]:
        parsed["next_agent"] = parsed["next_agent"].strip()

    # Validation rules by task
    if parsed["task"] == "continue":
        if not parsed["next_agent"] or parsed["next_agent"].upper() == "ALL":
            raise ValueError("CONTINUE task requires a specific NEXT AGENT")

    elif parsed["task"] == "request_speak_intent":
        parsed["next_agent"] = "ALL"

    elif parsed["task"] == "final_decision":
        parsed["next_agent"] = "Final Decision Agent"

    else:
        raise ValueError(f"Unknown SuperAgent task: {parsed['task']}")

    return parsed


class DebateMemory:
    MAX_MEMORY_LENGTH = 4000

    def check_debate_agents_memory_length_is_exceeded(self, state: DebateState):
        debate = state["debate"]
        model = state["model"]

        memory = build_memory(debate)
        token_count = model.get_num_tokens(memory)

        state["memory"] = memory

        return token_count > self.MAX_MEMORY_LENGTH, memory


    def refresh_debate_agents_memory(self, state: DebateState):
        debate = state["debate"]
        model = state["model"]

        messages: QuerySet[DebateMessage] = debate.debate_messages(return_queryset=True)

        last_ten_messages = messages[-10:]
        older_messages = messages[:-10]

        older_content = "\n".join(msg.content for msg in older_messages)

        prompt = SUMMARY_AGENT_PROMPT.format(
            PREVIOUS_SUMMARY=debate.summary or "",
            AGENT_HISTORY=older_content
        )

        response: AIMessage = model.invoke_with_log(prompt)
        new_summary = response.content.strip()

        debate.summary = new_summary
        debate.save()

        older_messages.update(is_memory_disabled=True)

        new_memory = new_summary + "\n" + "\n".join(msg.content for msg in last_ten_messages)

        return new_memory
    

    def get_memory(self, state : DebateState) -> str:
        is_exceeded, memory = self.check_debate_agents_memory_length_is_exceeded(state)
        if is_exceeded:
            memory = self.refresh_debate_agents_memory(state)
        return memory