from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    google_cloud_project: str = "promptwars-virtual2026"
    vertex_ai_location: str = "us-central1"
    firestore_database: str = "(default)"
    pubsub_topic_telemetry: str = "event-telemetry"
    pubsub_subscription: str = "event-telemetry-sub"
    gcs_docs_bucket: str = "eventflow-ai-docs-promptwars-virtual2026"
    gemini_model_flash: str = "gemini-2.5-flash"
    embedding_model: str = "text-embedding-004"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
