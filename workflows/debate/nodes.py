import logging
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from core_app.models import DebateMessage, Agent, Debate
from config import context_storage
from .schemas import DebateState
from .prompts import (
    AGENT_PROMPT,
    SUPER_AGENT_PROMPT,
    FINAL_DECISION_AGENT_PROMPT
)
from .utils import create_debate_message, parse_super_agent_response, DebateMemory

# =========================
# CONFIG
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

def green_log(message: str):
    GREEN = "\033[92m"   # Bright Green
    RESET = "\033[0m"
    BOLD = "\033[1m"

    border = "═" * 70
    prefix = "🟢 LOG"

    formatted_message = f"""
{GREEN}{BOLD}
╔{border}
║ {prefix}
╠{border}
    {message}

╚{border}
{RESET}
"""
    logging.info(formatted_message)

# =========================
# SUPER AGENT
# =========================


def conntect_org(state : DebateState):
    context_storage.set_current_org(state["org"])
    return state

def super_agent(state: DebateState):
    debate_memory = DebateMemory()
    debate = state["debate"]
    model = state["model"]
    memory = debate_memory.get_memory(state)
    super_agent = state["summary_agent"]

    prompt = SUPER_AGENT_PROMPT.format(
        MEMORY=memory,
        AGENTS=debate.agents_list()
    )

    response: AIMessage = model.invoke_with_log(prompt, agent_id = super_agent.id, org_id=state["org"].id)

    if state["_verbose"]:
        green_log("super_agent\n" + response.content)

    create_debate_message(
        content=response.content,
        debate=debate,
        agent=state["super_agent"],
        org = state['org']
    )

    state["super_agent_response"] = parse_super_agent_response(response.content)

    return state

# =========================
# SPEAK INTENT COLLECTION
# =========================

def request_speak_intent_agents(state: DebateState):
    debate_memory = DebateMemory()
    debate = state["debate"]
    model = state["model"]
    memory = debate_memory.get_memory(state)

    agents: list[Agent] = debate.agents.all()

    for agent in agents:
        system_prompt = AGENT_PROMPT.format(
            NAME=agent.name,
            ROLE=agent.role,
            GOAL=agent.goal,
            DOMAIN_EXPERTISE=agent.domain_expertise,
            DEBATE_STYLE=agent.debate_style,
            BACKSTORY=agent.backstory,
            MEMORY=memory,
            AGENT_DIRECTORY=debate.agents_list()
        )
        messages = [
            SystemMessage(system_prompt),
            HumanMessage("TASK 1 — SPEAK DECISION : Do you want to speak ?")
        ]
        response: AIMessage = model.invoke_with_log(messages, agent_id = agent.id, org_id=state["org"].id)
        if state["_verbose"]:
            green_log("request_speak_intent_agents\n" + response.content)

        create_debate_message(
            content=response.content,
            debate=debate,
            agent=agent,
            org = state['org']
        )

    return state

# =========================
# EXECUTE SELECTED AGENT
# =========================

def call_debate_agent(state: DebateState):
    debate_memory = DebateMemory()
    debate = state["debate"]
    model = state["model"]
    memory = debate_memory.get_memory(state)

    super_agent_data = state["super_agent_response"]
    next_agent_name = super_agent_data.get("next_agent")

    if not next_agent_name or next_agent_name.upper() == "NONE":
        return state

    agent : Agent = debate.agents.filter(name=next_agent_name).first()

    if not agent:
        raise ValueError(f"Agent '{next_agent_name}' not found in debate")

    system_prompt = AGENT_PROMPT.format(
        NAME=agent.name,
        ROLE=agent.role,
        GOAL=agent.goal,
        DOMAIN_EXPERTISE=agent.domain_expertise,
        DEBATE_STYLE=agent.debate_style,
        BACKSTORY=agent.backstory,
        MEMORY=memory,
        AGENT_DIRECTORY=debate.agents_list()
    )
    messages = [
        SystemMessage(system_prompt),
        HumanMessage("TASK 2 — FULL RESPONSE : Continue the debate with your inputs.")
    ]
    response: AIMessage = model.invoke_with_log(messages, agent_id = agent.id, org_id=state["org"].id)
    if state["_verbose"]:
        green_log(response.content)

    create_debate_message(
        content=response.content,
        debate=debate,
        agent=agent,
        org = state['org']
    )

    return state

# =========================
# FINAL DECISION AGENT
# =========================

def final_agent(state: DebateState):
    debate_memory = DebateMemory()
    debate = state["debate"]
    model = state["model"]
    memory = debate_memory.get_memory(state)
    final_decision_agent = state["final_decision_agent"]

    prompt = FINAL_DECISION_AGENT_PROMPT.format(
        MEMORY=memory,
        AGENTS=debate.agents_list()
    )

    response: AIMessage = model.invoke_with_log(prompt, agent_id = final_decision_agent.id, org_id=state["org"].id)
    if state["_verbose"]:
        green_log("final_agent\n" + response.content)

    create_debate_message(
        content=response.content,
        debate=debate,
        agent=state["final_decision_agent"],
        org = state['org']
    )

    return state
