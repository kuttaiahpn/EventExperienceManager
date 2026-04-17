from typing import Dict, Any
from services.pubsub_client import PubSubClient
import datetime

pubsub = PubSubClient()

async def publish_telemetry(event_id: str, payload_type: str, target_id: str, updates: Dict[str, Any]) -> str:
    """Publish a telemetry update to the events pubsub topic."""
    envelope = {
        "event_id": event_id,
        "source": "manager_sandbox",
        "priority": "high",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "payload_type": payload_type,
        "payload": {
            "target_id": target_id,
            "updates": updates
        }
    }
    await pubsub.publish_message(pubsub.settings.pubsub_topic_telemetry, envelope)
    return "published"
