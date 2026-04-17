from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from config import get_settings
from typing import List

class VertexAIClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def get_gemini_model(self) -> ChatVertexAI:
        return ChatVertexAI(
            model_name=self.settings.gemini_model_flash,
            project=self.settings.google_cloud_project,
            location=self.settings.vertex_ai_location,
        )

    def get_embedding_model(self) -> VertexAIEmbeddings:
        return VertexAIEmbeddings(
            model_name=self.settings.embedding_model,
            project=self.settings.google_cloud_project,
            location=self.settings.vertex_ai_location,
        )

    def embed_text(self, text: str) -> List[float]:
        embeddings = self.get_embedding_model()
        return embeddings.embed_query(text) # type: ignore
