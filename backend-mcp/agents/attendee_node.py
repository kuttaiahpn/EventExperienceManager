from langchain_core.messages import SystemMessage
from services.vertex_ai_client import VertexAIClient
from mcp_server.tools_venue import get_gate_status, get_zone_info, get_concession_info, get_facility_info, get_parking_status
from mcp_server.tools_knowledge import search_knowledge_base
from agents.state import AgentState
from langchain_core.tools import tool
from typing import Any, Optional, Dict, List

vertex_client = VertexAIClient()

@tool
async def lc_get_gate_status(event_id: str, gate_id: Optional[str] = None) -> Any:
    """Get status for all gates or a specific gate if gate_id is provided."""
    return await get_gate_status(event_id, gate_id)

@tool
async def lc_get_zone_info(event_id: str, zone_id: Optional[str] = None) -> Any:
    """Get information for all zones or a specific zone if zone_id is provided."""
    return await get_zone_info(event_id, zone_id)

@tool
async def lc_get_concession_info(event_id: str, stall_id: Optional[str] = None) -> Any:
    """Get information for all concessions or a specific stall if stall_id is provided."""
    return await get_concession_info(event_id, stall_id)

@tool
async def lc_get_facility_info(event_id: str, facility_id: Optional[str] = None) -> Any:
    """Get information for all facilities or a specific facility if facility_id is provided."""
    return await get_facility_info(event_id, facility_id)

@tool
async def lc_get_parking_status(event_id: str, lot_id: Optional[str] = None) -> Any:
    """Get parking status for all lots or a specific lot if lot_id is provided."""
    return await get_parking_status(event_id, lot_id)

@tool
async def lc_search_knowledge_base(query: str, limit: int = 5) -> Any:
    """Search the vector database for event policies and FAQs."""
    return await search_knowledge_base(query, limit)

ATTENDEE_TOOLS = [
    lc_get_gate_status, lc_get_zone_info, lc_get_concession_info, 
    lc_get_facility_info, lc_get_parking_status, lc_search_knowledge_base
]

def get_attendee_model() -> Any:
    model = vertex_client.get_gemini_model()
    return model.bind_tools(ATTENDEE_TOOLS)

async def attendee_node(state: AgentState) -> Dict[str, Any]:
    sys_msg = SystemMessage(content=(
        "You are an AI concierge for a live event at a 50,000-seat stadium. "
        "You help attendees with navigation, wait times, food recommendations, and event information. "
        "Use your tools to get real-time venue data and search the knowledge base for event policies and FAQs. "
        "Always provide specific, actionable guidance based on current conditions. "
        f"The current event context is: {state['event_id']}"
    ))
    
    messages = [sys_msg] + state["messages"] # type: ignore
    model = get_attendee_model()
    response = await model.ainvoke(messages)
    
    return {"messages": [response]}
