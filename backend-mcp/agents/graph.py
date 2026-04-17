from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from agents.state import AgentState
from agents.attendee_node import attendee_node, ATTENDEE_TOOLS
from agents.manager_node import manager_node, MANAGER_TOOLS
from typing import AsyncGenerator, Any, Dict

all_tools_dict: Dict[str, Any] = {}
for t in ATTENDEE_TOOLS + MANAGER_TOOLS:
    all_tools_dict[t.name] = t
all_tools = list(all_tools_dict.values())
tool_node = ToolNode(all_tools)

def route_persona(state: AgentState) -> str:
    if state["persona"] == "manager":
        return "manager_node"
    return "attendee_node"

def should_continue(state: AgentState, node_name: str) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END # type: ignore

def attendee_should_continue(state: AgentState) -> str:
    return should_continue(state, "attendee_node")

def manager_should_continue(state: AgentState) -> str:
    return should_continue(state, "manager_node")

workflow = StateGraph(AgentState)

workflow.add_node("attendee_node", attendee_node)
workflow.add_node("manager_node", manager_node)
workflow.add_node("tools", tool_node)

workflow.add_conditional_edges(START, route_persona, {
    "attendee_node": "attendee_node",
    "manager_node": "manager_node"
})

workflow.add_conditional_edges("attendee_node", attendee_should_continue, {
    "tools": "tools",
    END: END
})

workflow.add_conditional_edges("manager_node", manager_should_continue, {
    "tools": "tools",
    END: END
})

def route_back_from_tools(state: AgentState) -> str:
    return route_persona(state)

workflow.add_conditional_edges("tools", route_back_from_tools, {
    "attendee_node": "attendee_node",
    "manager_node": "manager_node"
})

checkpointer = MemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

async def invoke_graph(persona: str, session_id: str, event_id: str, message: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Streams the state updates from LangGraph"""
    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "messages": [("user", message)],
        "persona": persona,
        "event_id": event_id,
        "session_id": session_id
    }
    
    async for event in graph.astream_events(initial_state, config, version="v2"):
        yield event
