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
    """Sanitizes and maps human-readable names to Technical Firestore IDs using fuzzy matching."""
    if not raw_id:
        return raw_id
     
    import re
    # 1. Normalize: lowercase, remove special chars, use underscores
    # e.g. "Gate-D" -> "gate_d", "Zone 4" -> "zone_4"
    s = re.sub(r'[\s\-]+', '_', raw_id.strip().lower())
    
    # 2. Specific mappings for commonly misidentified stadium entities
    mapping = {
        "gate_a": "Gate_A", "gate_b": "Gate_B", "gate_c": "Gate_C",
        "gate_d": "Gate_D", "gate_e": "Gate_E", "gate_f": "Gate_F",
        "zone_a": "Zone_A", "zone_b": "Zone_B", "zone_c": "Zone_C",
        "zone_d": "Zone_D", "zone_e": "Zone_E",
        "north_parking": "Parking_North", "south_parking": "Parking_South", "east_parking": "Parking_East",
        "west_parking": "Parking_West", "parking_west": "Parking_West"
    }
    
    # 3. Try direct mapping
    if s in mapping:
        return mapping[s]
        
    # 4. Try fuzzy match for common typos (e.g. "gatea" -> "gate_a")
    if s.startswith("gate") and "_" not in s and len(s) > 4:
        s = f"gate_{s[4:]}"
    if s.startswith("zone") and "_" not in s and len(s) > 4:
        s = f"zone_{s[4:]}"
        
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
