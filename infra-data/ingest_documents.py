import os
import time
from typing import Any, List
from google.cloud import storage, firestore
from google.cloud.firestore_v1.vector import Vector
from langchain_google_vertexai import VertexAIEmbeddings # Correct Enterprise Library
import config

def ingest_documents() -> None:
    print(f"Connecting to GCS Bucket: {config.GCS_DOCS_BUCKET}")
    storage_client: storage.Client = storage.Client(project=config.GOOGLE_CLOUD_PROJECT)
    bucket = storage_client.bucket(config.GCS_DOCS_BUCKET)
    
    print(f"Connecting to Firestore: {config.GOOGLE_CLOUD_PROJECT}, database: {config.FIRESTORE_DATABASE}")
    db: firestore.Client = firestore.Client(project=config.GOOGLE_CLOUD_PROJECT, database=config.FIRESTORE_DATABASE)
    
    # Initialize Vertex AI Embeddings (matching the 768-dim index)
    print(f"Initializing Vertex AI Embeddings model: {config.EMBEDDING_MODEL}")
    embeddings_model = VertexAIEmbeddings(
        model_name=config.EMBEDDING_MODEL, 
        project=config.GOOGLE_CLOUD_PROJECT,
        location="us-central1"
    )
    
    blobs = bucket.list_blobs()
    total_chunks: int = 0
    
    for blob in blobs:
        name: str = blob.name.lower()
        if not name.endswith(".pdf"):
            continue
            
        print(f"Processing file: {blob.name}")
        temp_local_filename = f"temp_{blob.name}"
        
        try:
            blob.download_to_filename(temp_local_filename)
            
            from PyPDF2 import PdfReader
            text_content: str = ""
            with open(temp_local_filename, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted + "\n"
            
            if not text_content.strip():
                print(f"Warning: No text content found in {blob.name}")
                continue

            # CHUNKING: Essential to avoid token limits
            # Using 2000 character chunks as per user suggestion
            chunks = [text_content[i:i+2000] for i in range(0, len(text_content), 2000)]
            print(f"File split into {len(chunks)} chunks. Starting ingestion...")
            
            for i, chunk in enumerate(chunks):
                # RATE LIMITING: Prevent 429 RESOURCE_EXHAUSTED
                # 10s breather every 5 chunks as per user suggestion
                if i > 0 and i % 5 == 0:
                    print("Pausing 10s to respect API Quotas...")
                    time.sleep(10.0)
                
                # Generate Embedding
                embedding_vector: List[float] = embeddings_model.embed_query(chunk)
                
                # Store in Firestore (matching user's specific ingestion schema)
                db.collection("knowledge_base").add({
                    "file_name": blob.name,
                    "content": str(chunk),
                    "embedding": Vector(embedding_vector),  
                    "category": "faq",
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
                total_chunks += 1
                
            print(f"Successfully ingested: {blob.name}")

        except Exception as e:
            print(f"Error processing {blob.name}: {e}")
        finally:
            if os.path.exists(temp_local_filename):
                try:
                    os.remove(temp_local_filename)
                except:
                    pass
        
    print(f"Success: Ingested a total of {total_chunks} chunks.")

if __name__ == "__main__":
    ingest_documents()
