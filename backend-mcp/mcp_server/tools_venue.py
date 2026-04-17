from typing import Dict, Any, Optional
from services.firestore_client import FirestoreClient

firestore_client = FirestoreClient()

async def get_venue_state(event_id: str) -> Dict[str, Any]:
    """Get the full snapshot of the venue state including subcollections."""
    return await firestore_client.get_venue_state(event_id)

async def get_gate_status(event_id: str, gate_id: Optional[str] = None) -> Any:
    """Get status for all gates or a specific gate if gate_id is provided."""
    return await firestore_client.get_subcollection(event_id, "gates", gate_id)

async def get_zone_info(event_id: str, zone_id: Optional[str] = None) -> Any:
    """Get information for all zones or a specific zone if zone_id is provided."""
    return await firestore_client.get_subcollection(event_id, "zones", zone_id)

async def get_concession_info(event_id: str, stall_id: Optional[str] = None) -> Any:
    """Get information for all concessions or a specific stall if stall_id is provided."""
    return await firestore_client.get_subcollection(event_id, "concessions", stall_id)

async def get_facility_info(event_id: str, facility_id: Optional[str] = None) -> Any:
    """Get information for all facilities or a specific facility if facility_id is provided."""
    return await firestore_client.get_subcollection(event_id, "facilities", facility_id)

async def get_parking_status(event_id: str, lot_id: Optional[str] = None) -> Any:
    """Get parking status for all lots or a specific lot if lot_id is provided."""
    return await firestore_client.get_subcollection(event_id, "parking", lot_id)

def resolve_tech_id(collection: str, raw_id: str) -> str:
    """Sanitizes and maps human-readable names to Technical Firestore IDs."""
    if not raw_id:
        return raw_id
        
    s = raw_id.lower().replace(" ", "_").replace("-", "_")
    
    # Specific mappings for commonly misidentified stadium entities
    mapping = {
        "gate_a": "gate_a", "gate_b": "gate_b", "gate_c": "gate_c",
        "gate_d": "gate_d", "gate_e": "gate_e", "gate_f": "gate_f",
        "zone_a": "zone_a", "zone_b": "zone_b", "zone_c": "zone_c",
        "zone_d": "zone_d", "zone_e": "zone_e", "north_parking": "parking_north",
        "south_parking": "parking_south", "east_parking": "parking_east"
    }
    
    return mapping.get(s, s)

async def update_venue_state(event_id: str, collection: str, doc_id: str, updates: Dict[str, Any]) -> str:
    """Update a specific entity within the venue state (gates, zones, etc.)."""
    tech_id = resolve_tech_id(collection, doc_id)
    await firestore_client.update_subcollection_doc(event_id, collection, tech_id, updates)
    return f"success: updated {tech_id}"

async def get_simulation_controls(event_id: str) -> Dict[str, Any]:
    """Get simulation state from the top-level event document."""
    state = await firestore_client.get_venue_state(event_id)
    return state.get("simulation_controls", {}) # type: ignore
