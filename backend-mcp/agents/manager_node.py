from langchain_core.messages import SystemMessage
from services.vertex_ai_client import VertexAIClient
from mcp_server.tools_venue import get_venue_state, get_gate_status, get_zone_info, get_simulation_controls, update_venue_state
from mcp_server.server import log_event
from agents.state import AgentState
from langchain_core.tools import tool
from typing import Any, Optional, Dict

vertex_client = VertexAIClient()

@tool
async def lc_get_venue_state(event_id: str) -> Any:
    """Get the full snapshot of the venue state including subcollections."""
    return await get_venue_state(event_id)

@tool
async def lc_get_gate_status(event_id: str, gate_id: Optional[str] = None) -> Any:
    """Get status for all gates or a specific gate if gate_id is provided."""
    return await get_gate_status(event_id, gate_id)

@tool
async def lc_get_zone_info(event_id: str, zone_id: Optional[str] = None) -> Any:
    """Get information for all zones or a specific zone if zone_id is provided."""
    return await get_zone_info(event_id, zone_id)

@tool
async def lc_get_simulation_controls(event_id: str) -> Any:
    """Get simulation state from the top-level event document."""
    return await get_simulation_controls(event_id)

@tool
async def lc_update_venue_state(event_id: str, collection: str, doc_id: str, updates: Dict[str, Any]) -> Any:
    """Update a specific entity within the venue state (gates, zones, etc.)."""
    return await update_venue_state(event_id, collection, doc_id, updates)

@tool
async def lc_log_event(event_id: str, log_type: str, payload: Dict[str, Any], source: str) -> Any:
    """Log an operational event or significant action into the event_logs collection."""
    # Since python mcp wraps log_event as a tool with .invoke, we'll unwrap it for standard call
    # Actually wait, log_event in mcp_server/server.py is decorated with `@mcp.tool()`.
    # It might be safer to call firestore directly if FastMCP obscures the async.
    # From mcp.server.fastmcp, the original function is still callable or stored on mcp. 
    # Calling the decorated function might return coroutine or require context.
    from services.firestore_client import FirestoreClient
    return await FirestoreClient().write_event_log(event_id, log_type, payload, source)

MANAGER_TOOLS = [
    lc_get_venue_state, lc_get_gate_status, lc_get_zone_info, 
    lc_get_simulation_controls, lc_update_venue_state, lc_log_event
]

def get_manager_model() -> Any:
    model = vertex_client.get_gemini_model()
    return model.bind_tools(MANAGER_TOOLS)

async def manager_node(state: AgentState) -> Dict[str, Any]:
    sys_msg = SystemMessage(content=(
        "You are an AI operations analyst for a live event at a 50,000-seat stadium. "
        "You help event managers with crowd monitoring, anomaly detection, staff allocation, and risk assessment. "
        "Use your tools to analyze real-time venue telemetry and provide executive-level operational insights. "
        "CRITICAL: When updating the venue state (gates, zones, concessions), use the Technical IDs from the current state. "
        "Mapping reference: 'Gate A' -> 'gate_a', 'Gate B' -> 'gate_b', 'Gate C' -> 'gate_c', 'Gate D' -> 'gate_d', 'Gate E' -> 'gate_e', 'Gate F' -> 'gate_f'. "
        "Never create NEW documents for these entities; always update the existing Technical IDs. "
        f"The current event context is: {state['event_id']}"
    ))
    
    messages = [sys_msg] + state["messages"] # type: ignore
    model = get_manager_model()
    response = await model.ainvoke(messages)
    
    return {"messages": [response]}
