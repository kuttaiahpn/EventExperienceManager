from google.cloud import pubsub_v1
import json
from config import get_settings
from typing import Callable, Any, Dict
import asyncio
from concurrent.futures import Future

class PubSubClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()

    async def publish_message(self, topic: str, data_dict: Dict[str, Any]) -> None:
        topic_path = self.publisher.topic_path(self.settings.google_cloud_project, topic)
        data_str = json.dumps(data_dict)
        data_bytes = data_str.encode("utf-8")
        future = self.publisher.publish(topic_path, data_bytes)
        await asyncio.to_thread(future.result)

    def start_subscriber(self, callback: Callable[[pubsub_v1.subscriber.message.Message], None]) -> Any:
        subscription_path = self.subscriber.subscription_path(
            self.settings.google_cloud_project, 
            self.settings.pubsub_subscription
        )
        streaming_pull_future = self.subscriber.subscribe(subscription_path, callback=callback)
        return streaming_pull_future
