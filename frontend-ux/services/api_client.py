import os
import requests
import json
from sseclient import SSEClient
from typing import Dict, Any, Generator

class EventFlowAPI:
    def __init__(self, base_url: str = None):
        if not base_url:
            base_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
        self.base_url = base_url.rstrip("/")

    def chat(self, persona: str, session_id: str, message: str, event_id: str, context: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        url = f"{self.base_url}/api/v1/chat"
        payload = {
            "persona": persona,
            "session_id": session_id,
            "message": message,
            "event_id": event_id,
            "context": context
        }
        
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        client = SSEClient(response)
        for event in client.events():
            if event.data:
                try:
                    data = json.loads(event.data)
                    yield data
                except json.JSONDecodeError:
                    pass

    def simulate(self, event_id: str, anomaly_type: str, severity: int, target_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/simulate"
        payload = {
            "event_id": event_id,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "target_id": target_id,
            "manual_override_source": "manager_sandbox"
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_venue_state(self, event_id: str) -> dict:
        url = f"{self.base_url}/api/v1/venue-state/{event_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
