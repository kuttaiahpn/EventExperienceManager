import json
import os
from typing import Any, Dict, List
from google.cloud import firestore  # type: ignore

import config

def load_json(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, 'r') as f:
        return json.load(f)

def seed_database() -> None:
    print(f"Connecting to Firestore project: {config.GOOGLE_CLOUD_PROJECT}, database: {config.FIRESTORE_DATABASE}")
    db: firestore.Client = firestore.Client(project=config.GOOGLE_CLOUD_PROJECT, database=config.FIRESTORE_DATABASE)
    
    venue_ref = db.collection("venue_state").document("STADIUM_2026_01")
    
    seed_dir: str = os.path.join(os.path.dirname(__file__), "seed_data")
    
    gates_data: List[Dict[str, Any]] = load_json(os.path.join(seed_dir, "gates.json"))
    zones_data: List[Dict[str, Any]] = load_json(os.path.join(seed_dir, "zones.json"))
    concessions_data: List[Dict[str, Any]] = load_json(os.path.join(seed_dir, "concessions.json"))
    facilities_data: List[Dict[str, Any]] = load_json(os.path.join(seed_dir, "facilities.json"))
    parking_data: List[Dict[str, Any]] = load_json(os.path.join(seed_dir, "parking.json"))
    
    try:
        batch = db.batch()
        
        # 1. Base Event Document
        event_metadata: Dict[str, Any] = {
            "event_id": "STADIUM_2026_01",
            "event_type": "concert",
            "current_stage": "pre_event",
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        simulation_controls: Dict[str, Any] = {
            "is_anomaly_active": False,
            "active_risk_factor": "none",
            "manual_override_source": None,
            "target_stage": None
        }
        
        batch.set(venue_ref, {
            "event_metadata": event_metadata,
            "simulation_controls": simulation_controls
        })
        
        # 2. Subcollections
        for gate in gates_data:
            doc_ref = venue_ref.collection("gates").document(gate["gate_id"])
            batch.set(doc_ref, gate)
            
        for zone in zones_data:
            doc_ref = venue_ref.collection("zones").document(zone["zone_id"])
            batch.set(doc_ref, zone)
            
        for concession in concessions_data:
            doc_ref = venue_ref.collection("concessions").document(concession["stall_id"])
            batch.set(doc_ref, concession)
            
        for facility in facilities_data:
            doc_ref = venue_ref.collection("facilities").document(facility["facility_id"])
            batch.set(doc_ref, facility)
            
        for parking in parking_data:
            doc_ref = venue_ref.collection("parking").document(parking["lot_id"])
            batch.set(doc_ref, parking)
            
        # Commit all writes
        batch.commit()
        print("Success: Seed data written to Firestore.")
    except Exception as e:
        print(f"Failure: Error seeding database: {e}")

if __name__ == "__main__":
    seed_database()
