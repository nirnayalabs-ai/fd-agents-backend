from langgraph.graph import StateGraph, START, END
from .schemas import DebateState
from .nodes import (
    conntect_org,
    super_agent,
    request_speak_intent_agents,
    call_debate_agent,
    final_agent,
)

# ============================
# Initialize Debate Workflow
# ============================

workflow = StateGraph(DebateState)

# ============================
# Nodes (Human-Readable Names)
# ============================

workflow.add_node("Connect to Current Organization", conntect_org)
workflow.add_node("Super Agent Decision", super_agent)
workflow.add_node("Collect Speak Intentions", request_speak_intent_agents)
workflow.add_node("Execute Debate Turn", call_debate_agent)
workflow.add_node("Generate Final Decision", final_agent)

# ============================
# Edges (Straight Flow)
# ============================
workflow.add_edge(START, "Connect to Current Organization")
workflow.add_edge("Connect to Current Organization", "Super Agent Decision")
workflow.add_edge("Collect Speak Intentions", "Super Agent Decision")
workflow.add_edge("Execute Debate Turn", "Super Agent Decision")
workflow.add_edge("Generate Final Decision", END)

# ============================
# Conditional Routing Logic
# ============================

def route_by_super_agent_task(state: DebateState) -> str:
    """
    Routes workflow based on SuperAgent PAS decision.
    """
    task : str = state["super_agent_response"].get("task")

    if not task:
        raise ValueError("SuperAgent response missing TASK")

    return task.lower()

workflow.add_conditional_edges(
    "Super Agent Decision",
    route_by_super_agent_task,
    {
        "continue": "Execute Debate Turn",
        "request_speak_intent": "Collect Speak Intentions",
        "final_decision": "Generate Final Decision",
    }
)

# ============================
# Compile Graph
# ============================

debate_graph = workflow.compile()

# ============================
# Visualize Graph
# ============================

graph_png = debate_graph.get_graph(xray=True).draw_mermaid_png()
image_file = "Debate Workflow.png"

with open(image_file, "wb") as file:
    file.write(graph_png)
