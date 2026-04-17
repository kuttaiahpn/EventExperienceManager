import os
from typing import Optional

def get_env_var(name: str, default_val: Optional[str] = None) -> str:
    val = os.getenv(name, default_val)
    if val is None:
        raise ValueError(f"Environment variable {name} is not set and no default provided.")
    return val

GOOGLE_CLOUD_PROJECT: str = get_env_var("GOOGLE_CLOUD_PROJECT", "promptwars-virtual2026")
VERTEX_AI_LOCATION: str = get_env_var("VERTEX_AI_LOCATION", "us-central1")
FIRESTORE_DATABASE: str = get_env_var("FIRESTORE_DATABASE", "(default)")
PUBSUB_TOPIC_TELEMETRY: str = get_env_var("PUBSUB_TOPIC_TELEMETRY", "event-telemetry")
GCS_DOCS_BUCKET: str = get_env_var("GCS_DOCS_BUCKET", "eventflow-ai-docs-promptwars-virtual2026")
EMBEDDING_MODEL: str = get_env_var("EMBEDDING_MODEL", "text-embedding-004")
