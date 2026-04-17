import json
import time
import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict

from google.cloud import pubsub_v1  # type: ignore

import config

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

def run_health_server() -> None:
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print("Starting health check server on port 8080...")
    httpd.serve_forever()

def publish_message(publisher: pubsub_v1.PublisherClient, topic_path: str, payload_type: str, target_id: str, updates: Dict[str, Any]) -> None:
    message: Dict[str, Any] = {
        "event_id": "STADIUM_2026_01",
        "source": "baseline_engine",
        "priority": "normal",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "payload_type": payload_type,
        "payload": {
            "target_id": target_id,
            "updates": updates
        }
    }
    
    data_str = json.dumps(message)
    data = data_str.encode("utf-8")
    
    try:
        future = publisher.publish(topic_path, data)
        future.result()
        print(f"[{message['timestamp']}] Published {payload_type} for {target_id}")
    except Exception as e:
        print(f"Error publishing message: {e}")

def run_scenario_engine() -> None:
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(config.GOOGLE_CLOUD_PROJECT, config.PUBSUB_TOPIC_TELEMETRY)
    
    print(f"Starting Scenario Engine. Publishing to {topic_path} every 30s")
    
    stages = ["pre_event", "entry", "during", "exit"]
    stage_duration_seconds = 2.5 * 60  # 150 seconds per stage
    
    current_stage_index = 0
    start_time = time.time()
    
    # Send initial transition
    publish_message(publisher, topic_path, "stage_transition", "stadium", {"new_stage": stages[current_stage_index]})
    
    while True:
        now = time.time()
        elapsed = now - start_time
        
        # Check if we should transition to next stage
        if elapsed >= stage_duration_seconds:
            start_time = now
            current_stage_index = (current_stage_index + 1) % len(stages)
            new_stage = stages[current_stage_index]
            print(f"\n--- Transitioning to stage: {new_stage} ---\n")
            publish_message(publisher, topic_path, "stage_transition", "stadium", {"new_stage": new_stage})
        
        current_stage = stages[current_stage_index]
        
        # Determine metrics based on stage
        if current_stage == "pre_event":
            # pre_event: low occupancy, all gates open, parking filling
            publish_message(publisher, topic_path, "gate_update", "Gate_A", {"occupancy_rate": 0.05, "status": "open", "avg_wait_time_mins": 0})
            publish_message(publisher, topic_path, "parking_update", "North_Lot", {"occupancy_rate": 0.3, "status": "filling"})
            
        elif current_stage == "entry":
            # entry: gates getting busy, parking filling up, concessions opening
            publish_message(publisher, topic_path, "gate_update", "Gate_B", {"occupancy_rate": 0.7, "status": "open", "avg_wait_time_mins": 10})
            publish_message(publisher, topic_path, "parking_update", "South_Lot", {"occupancy_rate": 0.8, "status": "filling"})
            publish_message(publisher, topic_path, "concession_update", "Taco_Vibe_01", {"is_active": True, "stock_level": "optimal"})
            
        elif current_stage == "during":
            # during: peak crowd, wait times, concession stocks depleting
            publish_message(publisher, topic_path, "zone_update", "Section_103", {"crowd_density": "high", "washroom_wait_mins": 15})
            publish_message(publisher, topic_path, "concession_update", "BBQ_Pit_01", {"is_active": True, "stock_level": "depleted", "avg_prep_time_mins": 20})
            
        elif current_stage == "exit":
            # exit: gates clearing, parking clearing, facilities winding down
            publish_message(publisher, topic_path, "gate_update", "Gate_A", {"occupancy_rate": 0.4, "status": "open", "avg_wait_time_mins": 2})
            publish_message(publisher, topic_path, "parking_update", "East_Lot", {"occupancy_rate": 0.6, "status": "clearing"})
            publish_message(publisher, topic_path, "facility_update", "Restroom_L1_West", {"status": "maintenance"})
            
        time.sleep(30)

if __name__ == "__main__":
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    run_scenario_engine()
