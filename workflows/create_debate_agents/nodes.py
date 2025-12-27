import logging
from langchain_core.messages import AIMessage
from .schemas import DebateAgentsCreationState
from .prompts import INITIAL_AGENTS_CREATION_PROMPT, AGENT_EXPANSION_PROMPT
from config import context_storage


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

def conntect_org(state : DebateAgentsCreationState):
    context_storage.set_current_org(state["org"])
    return state


def init_initial_agents_creation_prompt(state: DebateAgentsCreationState):
    _verbose = state['_verbose']
    if _verbose:
        green_log("🚀 Starting Initial Agent Creation workflow")

    user_topic = state['user_topic']    
    initial_agents_prompt = INITIAL_AGENTS_CREATION_PROMPT.format(USER_TOPIC=user_topic)
    state['initial_agents_prompt'] = initial_agents_prompt
    return state
            

def call_model_for_initial_agents(state: DebateAgentsCreationState):
    _verbose = state['_verbose']
    if _verbose:
        green_log("🤖 Calling model for initial agents creation")
    
    model = state['model']
    initial_agents_prompt = state['initial_agents_prompt']
    response : AIMessage = model.invoke_with_log(initial_agents_prompt)

    if _verbose:
        green_log("✅ Initial agents created")
        green_log(f"Response: \n{response.content}")

    if "\n\n" in response.content:
        initial_agents = response.content.split("\n\n")
    elif "\nEND" in response.content:
        initial_agents = response.content.split("\nEND")[:-1]
    else:
        initial_agents = response.content.split("AGENT\n")[1:]

    if len(initial_agents[-1]) < 10:
        initial_agents.pop(-1) 
    elif len(initial_agents[0]) < 10:
        initial_agents.pop(0) 
    
    state['initial_agents'] = initial_agents
    return state 
    

def init_agent_expansion_prompt(state: DebateAgentsCreationState):
    current_index = state['current_initial_agent_index']
    initial_agent = state['initial_agents'][current_index].strip()
    user_topic = state['user_topic']
    agent_expansion_prompt = AGENT_EXPANSION_PROMPT.format(
        USER_TOPIC=user_topic,
        BASE_AGENT=initial_agent
    )
    state['agent_expansion_prompt'] = agent_expansion_prompt
    return state
    
def call_model_for_agent_expansion(state: DebateAgentsCreationState):
    _verbose = state['_verbose']
    if _verbose:
        green_log("🤖 Calling model for agent expansion")
    
    model = state['model']
    agent_expansion_prompt = state['agent_expansion_prompt']
    response : AIMessage = model.invoke_with_log(agent_expansion_prompt)

    if _verbose:
        green_log("✅ Agent expanded")
        green_log(f"Response: \n{response.content}")

    expanded_agents = state['expanded_agents']
    expanded_agents.append(response.content)
    state['expanded_agents'] = expanded_agents
    return state

def increment_initial_agent_index(state: DebateAgentsCreationState):
    current_index = state['current_initial_agent_index']
    state['current_initial_agent_index'] = current_index + 1
    return state
