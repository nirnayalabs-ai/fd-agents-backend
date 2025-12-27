from typing_extensions import TypedDict
from helper.classes import LLMModel

class DebateAgentsCreationState(TypedDict):
    model : LLMModel
    user_topic: str
    initial_agents_prompt: str
    agent_expansion_prompt: str
    initial_agents: list[str]
    current_initial_agent_index: int
    expanded_agents: list[str]
    _verbose: bool
