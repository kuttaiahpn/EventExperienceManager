from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from typing import Any, Dict, List, Optional
import datetime
from config import get_settings

class FirestoreClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.db: firestore.AsyncClient = firestore.AsyncClient(
            project=settings.google_cloud_project,
            database=settings.firestore_database
        )

    async def get_venue_state(self, event_id: str) -> Dict[str, Any]:
        doc_ref = self.db.collection("venue_state").document(event_id)
        doc = await doc_ref.get()
        state = doc.to_dict() or {}
        
        # Fetch subcollections
        for sub_name in ["gates", "zones", "concessions", "facilities", "parking"]:
            sub_docs = await doc_ref.collection(sub_name).get()
            state[sub_name] = {d.id: d.to_dict() for d in sub_docs}
            
        return state

    async def get_subcollection(self, event_id: str, collection_name: str, doc_id: Optional[str] = None) -> Any:
        col_ref = self.db.collection("venue_state").document(event_id).collection(collection_name)
        if doc_id:
            doc = await col_ref.document(doc_id).get()
            if doc.exists:
                return dict(id=doc.id, **(doc.to_dict() or {}))
            return None
        else:
            docs = await col_ref.get()
            return [dict(id=d.id, **(d.to_dict() or {})) for d in docs]

    async def update_subcollection_doc(self, event_id: str, collection_name: str, doc_id: str, updates: Dict[str, Any]) -> None:
        doc_ref = self.db.collection("venue_state").document(event_id).collection(collection_name).document(doc_id)
        await doc_ref.set(updates, merge=True)

    async def update_event_metadata(self, event_id: str, updates: Dict[str, Any]) -> None:
        doc_ref = self.db.collection("venue_state").document(event_id)
        await doc_ref.set({"event_metadata": updates}, merge=True)

    async def update_simulation_controls(self, event_id: str, updates: Dict[str, Any]) -> None:
        doc_ref = self.db.collection("venue_state").document(event_id)
        await doc_ref.set({"simulation_controls": updates}, merge=True)

    async def vector_search(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        col_ref = self.db.collection("knowledge_base")
        vector_query = col_ref.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_embedding),
            distance_measure=firestore.DistanceMeasure.COSINE,
            limit=limit
        )
        results = await vector_query.get()
        return [doc.to_dict() or {} for doc in results]

    async def write_event_log(self, event_id: str, log_type: str, payload: Dict[str, Any], source: str) -> None:
        col_ref = self.db.collection("event_logs")
        await col_ref.add({
            "event_id": event_id,
            "log_type": log_type,
            "payload": payload,
            "source": source,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        })
