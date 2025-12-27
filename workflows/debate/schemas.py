from typing_extensions import TypedDict
from helper.classes import LLMModel
from core_app.models import Debate, Agent
from orgs_app.models import Organization

class DebateState(TypedDict):
    model : LLMModel
    debate: Debate
    summary_agent : Agent
    super_agent : Agent
    final_decision_agent : Agent
    memory : str
    super_agent_response : dict
    org : Organization
    _verbose: bool
