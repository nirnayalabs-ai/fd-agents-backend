from langgraph.graph import StateGraph, START, END
from .schemas import DebateAgentsCreationState
from .nodes import (
    conntect_org,
    init_initial_agents_creation_prompt,
    call_model_for_initial_agents,
    init_agent_expansion_prompt,
    call_model_for_agent_expansion,
    increment_initial_agent_index
)

# ============================
# Build Graph
# ============================

workflow = StateGraph(DebateAgentsCreationState)

# ----------------------------
# Nodes
# ----------------------------
workflow.add_node("Connect to Current Organization", conntect_org)
workflow.add_node("Prepare Initial Agents Prompt", init_initial_agents_creation_prompt)
workflow.add_node("Generate Initial Agents", call_model_for_initial_agents)
workflow.add_node("Prepare Agent Expansion Prompt", init_agent_expansion_prompt)
workflow.add_node("Expand Single Agent", call_model_for_agent_expansion)
workflow.add_node("Move To Next Agent", increment_initial_agent_index)

# ----------------------------
# Edges (Readable transitions)
# ----------------------------
workflow.add_edge(START, "Connect to Current Organization")
workflow.add_edge("Connect to Current Organization", "Prepare Initial Agents Prompt")
workflow.add_edge("Prepare Initial Agents Prompt", "Generate Initial Agents")
workflow.add_edge("Generate Initial Agents", "Prepare Agent Expansion Prompt")
workflow.add_edge("Prepare Agent Expansion Prompt", "Expand Single Agent")
workflow.add_edge("Expand Single Agent", "Move To Next Agent")

# ----------------------------
# Conditional Logic
# ----------------------------
def should_continue_expansion(state: DebateAgentsCreationState):
    return (
        "STOP"
        if state["current_initial_agent_index"] >= len(state["initial_agents"])
        else "CONTINUE"
    )

workflow.add_conditional_edges(
    "Move To Next Agent",
    should_continue_expansion,
    {
        "CONTINUE": "Prepare Agent Expansion Prompt",
        "STOP": END,
    }
)

# ----------------------------
# Compile Graph
# ----------------------------
debate_agents_creation_graph = workflow.compile()

# ----------------------------
# Visualize Graph
# ----------------------------
graph_png = debate_agents_creation_graph.get_graph(xray=True).draw_mermaid_png()
image_file = "Debate Agents Creation Workflow.png"
with open(image_file, "wb") as file:
    file.write(graph_png)


