from langgraph.graph import START, StateGraph
from typing import TypedDict

class ParentState(TypedDict):
    foo: str

def node_1(state: ParentState):
    return {"foo": "hi! " + state["foo"]}

def node_2(state: ParentState):
    return {"foo": "hi! " + state["foo"] + " from node 2"}

builder = StateGraph(ParentState)
builder.add_node("node_1", node_1)
builder.add_node("node__2", node_2)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node__2")
graph = builder.compile()

for chunk in graph.stream(
    {"foo": "foo"},
    stream_mode="updates",
):
    print(chunk)