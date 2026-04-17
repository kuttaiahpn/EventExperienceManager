from fastapi import APIRouter
from pydantic import BaseModel
from services.pubsub_client import PubSubClient
import datetime
from typing import Optional, Dict, Any

router = APIRouter()
pubsub = PubSubClient()

class SimulateRequest(BaseModel):
    event_id: str
    anomaly_type: str
    severity: int          # int, not str — frontend sends integers
    target_id: str
    manual_override_source: Optional[str] = "manager_sandbox"

# Map anomaly_type to the correct Pub/Sub payload_type the subscriber understands
_ANOMALY_PAYLOAD_TYPE: Dict[str, str] = {
    "gate_failure": "gate_update",
    "gate_recovery": "gate_update",
    "surge": "zone_update",
    "vendor_slowdown": "concession_update",
    "facility_closure": "facility_update", # New mapping
    "weather_delay": "anomaly_inject",
    "stage_transition": "stage_transition",
}

@router.post("/simulate")
async def simulate_endpoint(body: SimulateRequest) -> Dict[str, Any]:
    payload_type = _ANOMALY_PAYLOAD_TYPE.get(body.anomaly_type, "anomaly_inject")

    # Build updates dict contextually
    if payload_type == "gate_update":
        updates: Dict[str, Any] = {
            "status": "closed" if body.anomaly_type == "gate_failure" else "open",
            "anomaly_alert": f"Manager override: {body.anomaly_type}" if body.anomaly_type == "gate_failure" else None,
        }
    elif payload_type == "zone_update":
        density = "critical" if body.severity >= 80 else "high" if body.severity >= 50 else "medium"
        updates = {"crowd_density": density}
    elif payload_type == "concession_update":
        # Ensure 'is_active' is toggled so the UI icon turns Red during slowdowns
        updates = {
            "avg_prep_time_mins": body.severity,
            "is_active": body.severity < 25 # Mark as inactive/overwhelmed if wait > 25m
        }
    elif payload_type == "facility_update":
        updates = {
            "status": "closed" if body.severity > 0 else "open",
            "wait_time_mins": body.severity
        }
    elif payload_type == "stage_transition":
        updates = {"new_stage": body.target_id}   # target_id carries the stage name
    else:
        updates = {
            "anomaly_type": body.anomaly_type,
            "severity": body.severity,
            "manual_override_source": body.manual_override_source,
            "is_anomaly_active": body.severity > 0,
            "active_risk_factor": body.anomaly_type if body.severity > 0 else "none",
        }

    envelope = {
        "event_id": body.event_id,
        "source": "manager_sandbox",
        "priority": "high",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "payload_type": payload_type,
        "payload": {
            "target_id": body.target_id,
            "updates": updates,
        },
    }

    await pubsub.publish_message(pubsub.settings.pubsub_topic_telemetry, envelope)

    return {
        "status": "published",
        "timestamp": envelope["timestamp"],
    }
