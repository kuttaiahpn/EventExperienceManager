from mcp.server.fastmcp import FastMCP
from mcp_server.tools_venue import (
    get_venue_state, get_gate_status, get_zone_info, get_concession_info,
    get_facility_info, get_parking_status, update_venue_state, get_simulation_controls
)
from mcp_server.tools_knowledge import search_knowledge_base
from mcp_server.tools_pubsub import publish_telemetry
from services.firestore_client import FirestoreClient
from typing import Dict, Any

mcp = FastMCP("EventFlowAI")

mcp.tool()(get_venue_state)
mcp.tool()(get_gate_status)
mcp.tool()(get_zone_info)
mcp.tool()(get_concession_info)
mcp.tool()(get_facility_info)
mcp.tool()(get_parking_status)
mcp.tool()(update_venue_state)
mcp.tool()(get_simulation_controls)
mcp.tool()(search_knowledge_base)
mcp.tool()(publish_telemetry)

firestore_client = FirestoreClient()

@mcp.tool()
async def log_event(event_id: str, log_type: str, payload: Dict[str, Any], source: str) -> str:
    """Log an operational event or significant action into the event_logs collection."""
    await firestore_client.write_event_log(event_id, log_type, payload, source)
    return "logged"
