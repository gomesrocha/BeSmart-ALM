"""Embeddings generation using Ollama."""
import httpx
from typing import List
import numpy as np


class EmbeddingsClient:
    """Client for generating embeddings using Ollama."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "nomic-embed-text:latest"
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("embedding", [])
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    async def find_most_relevant(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[tuple[str, float]]:
        """Find most relevant documents for a query using semantic search."""
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)
        
        # Generate document embeddings
        doc_embeddings = await self.generate_embeddings(documents)
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(doc_embeddings):
            similarity = self.cosine_similarity(query_embedding, doc_embedding)
            similarities.append((documents[i], similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
