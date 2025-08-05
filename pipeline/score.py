from langchain_cohere import CohereRerank, CohereEmbeddings
from rank_bm25 import BM25Okapi
from config.qdrant import QdrantConfig
from langchain.schema import Document
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ScoreCandidates:

    def score(record: dict):
        job_id = record.get("job_id")
        application_text = record.get("text")
        if not job_id or not application_text:
            return False
        
        qdrant = QdrantConfig(collection="job_descriptions")
        
        result = qdrant.get_job_with_filter(job_id)

        job_description_point = result[0][0]

        job_vector = job_description_point.vector

        cohere_embeddings = CohereEmbeddings(model="embed-english-light-v3.0")
        embeddings = cohere_embeddings.embed_query(application_text)

        # bm25_score = ScoreCandidates.bm25_score(job_description_point.payload["page_content"], application_text)
        rerank_score = ScoreCandidates.rerank_score(job_description_point.payload["page_content"], application_text)
        cosine_similarity_score = ScoreCandidates.cosine_similarity(job_vector, embeddings)

        # final_score = round(((rerank_score + cosine_similarity_score) / 2), 3)
        final_score = round((0.7 * rerank_score + 0.3 * cosine_similarity_score), 3)

        print(f"Final score for application id: {record.get("application_id")} for job_id {job_id}: {final_score}")
        return final_score

    # def bm25_score(job_text, application_text):
    #     tokenized_job_text = [doc.split(" ") for doc in job_text]

    #     bm25_model = BM25Okapi(tokenized_job_text)

    #     tokenized_application_text = application_text.split(" ")

    #     score = bm25_model.get_scores(tokenized_application_text)

    #     return score
    
    def rerank_score(job_description: str, application_text: str):
        try:
            reranker = CohereRerank(model="rerank-english-v3.0")

            result = reranker.rerank(
                query=job_description,
                documents=[application_text],
                top_n=1
            )

            return result[0]["relevance_score"]
        except Exception as e:
            print(f"Error in reranking: {e}")
            return 0.0
    
    def normalize(vec):
        norm = np.linalg.norm(vec)
        return vec / norm if norm != 0 else vec

    def cosine_similarity(vec1, vec2):
        vec1 = ScoreCandidates.normalize(np.array(vec1)).reshape(1, -1)
        vec2 = ScoreCandidates.normalize(np.array(vec2)).reshape(1, -1)
        return float(cosine_similarity(vec1, vec2)[0][0])
