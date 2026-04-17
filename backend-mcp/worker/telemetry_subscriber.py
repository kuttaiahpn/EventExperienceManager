import json
import logging
import asyncio
from typing import Callable, Coroutine, Any
from google.cloud import pubsub_v1
from services.firestore_client import FirestoreClient

logger = logging.getLogger(__name__)

async def process_message(message_data: dict[str, Any], firestore_client: FirestoreClient) -> None:
    try:
        event_id = message_data.get("event_id")
        payload_type = message_data.get("payload_type")
        payload = message_data.get("payload", {})
        source = message_data.get("source", "unknown")
        
        target_id = payload.get("target_id")
        updates = payload.get("updates", {})
        
        if not event_id or not payload_type:
            logger.error(f"Missing event_id or payload_type in message: {message_data}")
            return

        if payload_type == "gate_update":
            if target_id:
                await firestore_client.update_subcollection_doc(event_id, "gates", target_id, updates)
        elif payload_type == "zone_update":
            if target_id:
                await firestore_client.update_subcollection_doc(event_id, "zones", target_id, updates)
        elif payload_type == "concession_update":
            if target_id:
                await firestore_client.update_subcollection_doc(event_id, "concessions", target_id, updates)
        elif payload_type == "facility_update":
            if target_id:
                await firestore_client.update_subcollection_doc(event_id, "facilities", target_id, updates)
        elif payload_type == "parking_update":
            if target_id:
                await firestore_client.update_subcollection_doc(event_id, "parking", target_id, updates)
        elif payload_type == "stage_transition":
            await firestore_client.update_event_metadata(event_id, {"current_stage": updates.get("new_stage")})
        elif payload_type == "anomaly_inject":
            await firestore_client.update_simulation_controls(event_id, updates)
        else:
            logger.warning(f"Unknown payload_type: {payload_type}")
            
        await firestore_client.write_event_log(event_id, payload_type, payload, source)
        logger.info(f"Successfully processed {payload_type} for event {event_id}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")

def get_callback(firestore_client: FirestoreClient, loop: asyncio.AbstractEventLoop) -> Callable[[pubsub_v1.subscriber.message.Message], None]:
    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        try:
            data = json.loads(message.data.decode("utf-8"))
            asyncio.run_coroutine_threadsafe(process_message(data, firestore_client), loop)
            message.ack()
        except Exception as e:
            logger.error(f"Failed to decode or process pubsub message: {e}")
            message.nack()
    return callback

def start_subscriber_worker() -> None:
    from services.pubsub_client import PubSubClient
    loop = asyncio.get_event_loop()
    pubsub = PubSubClient()
    firestore_client = FirestoreClient()

    future = pubsub.start_subscriber(get_callback(firestore_client, loop))
    # Store on module level so it is never garbage-collected
    import sys
    setattr(sys.modules[__name__], "_streaming_pull_future", future)
    logger.info("Started Telemetry Subscriber background worker.")
