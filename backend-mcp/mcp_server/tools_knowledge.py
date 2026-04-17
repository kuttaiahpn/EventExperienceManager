from typing import List, Dict, Any
from services.firestore_client import FirestoreClient
from services.vertex_ai_client import VertexAIClient

firestore_client = FirestoreClient()
vertex_client = VertexAIClient()

async def search_knowledge_base(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search the vector database for event policies and FAQs over the knowledge base."""
    try:
        # embed the query
        if not query or not query.strip():
            return []
            
        embedding = vertex_client.embed_text(query)
        if not embedding:
            return []
            
        # search firestore
        results = await firestore_client.vector_search(embedding, limit)
        return results
    except Exception as e:
        print(f"Error in search_knowledge_base: {e}")
        # Return empty list instead of crashing, allowing the agent to handle the failure gracefully
        return []
