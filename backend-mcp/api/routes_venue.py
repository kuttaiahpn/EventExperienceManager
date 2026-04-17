from fastapi import APIRouter
from services.firestore_client import FirestoreClient
from typing import Dict, Any

router = APIRouter()
firestore_client = FirestoreClient()

@router.get("/venue-state/{event_id}")
async def get_venue_state_endpoint(event_id: str) -> Dict[str, Any]:
    state = await firestore_client.get_venue_state(event_id)
    return state
