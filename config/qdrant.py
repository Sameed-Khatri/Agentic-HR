from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()

class QdrantConfig:

    def __init__(self, collection: str):
        self.client = QdrantClient(url="http://localhost:6333", api_key=os.getenv("QDRANT_API_KEY"), check_compatibility=False)
        self.collection = collection
        
    def get_vector_store(self) -> QdrantVectorStore:
        return QdrantVectorStore(
            client=self.client,
            collection_name=self.collection,
            embedding=CohereEmbeddings(model="embed-english-light-v3.0"),
            content_payload_key="page_content",
            metadata_payload_key="metadata"
        )
    
    def get_client(self) -> QdrantClient:
        return self.client
    
    def get_job_with_filter(self, job_id: str):
        result = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.job_id",
                        match=models.MatchValue(value=job_id)
                    )
                ]
            ),
            with_payload=True,
            with_vectors=True,
            limit=1
        )
        return result
    
    def get_all_jobs(self, batch_size: int = 2):
        all_results = []
        offset = None

        while True:
            result = self.client.scroll(
                collection_name=self.collection,
                with_payload=True,
                with_vectors=False,
                limit=batch_size,
                offset=offset
            )

            points = result[0]
            next_offset = result[1]

            if not points:
                break

            all_results.extend(points)

            if next_offset is None:
                break

            offset = next_offset

        return all_results
    
    def get_top_candidates(self, job_id: str, top_n: int = 5):
        result = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.job_id",
                        match=models.MatchValue(value=job_id)
                    )
                ]
            ),
            with_payload=True,
            with_vectors=False,
            limit=top_n
        )

        points = result[0]

        sorted_points = sorted(
            points,
            key=lambda x: x.payload.get("metadata", {}).get("score", -1),
            reverse=True
        )
        return sorted_points[:top_n]