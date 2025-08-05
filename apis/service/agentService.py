from config.qdrant import QdrantConfig
from agent.graph import Graph

class Service:

    def load_all_jobs():
        all_results = []

        qdrant = QdrantConfig(collection="job_descriptions")
        results = qdrant.get_all_jobs()

        for result in results:
            payload = result.payload
            job_description = payload.get("page_content", "")
            metadata = payload.get("metadata", {})
            job = {
                "description": job_description,
                **metadata
            }

            all_results.append(job)

        # print(all_results)
        print(f"Total jobs loaded: {len(all_results)}")
        return all_results
    
    def load_top_candidates(job_id: str, top_n: int = 5):
        all_results = []

        qdrant = QdrantConfig(collection="candidate_applications")
        results = qdrant.get_top_candidates(job_id=job_id, top_n=top_n)

        for result in results:
            payload = result.payload
            candidate_description = payload.get("page_content", "")
            metadata = payload.get("metadata", {})
            candidate = {
                "description": candidate_description,
                **metadata
            }

            all_results.append(candidate)
        
        # print(all_results)
        print(f"Total candidates loaded for job {job_id}: {len(all_results)}")
        return all_results

    def invoke_agents(state: dict, thread_id: str):
        result = Graph.invoke_agents(state=state, thread_id=thread_id)
        return result