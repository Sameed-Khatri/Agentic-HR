from config.qdrant import QdrantConfig
from langchain_community.document_loaders import JSONLoader
from pipeline.score import ScoreCandidates
import time

class DocumentLoader:
    ITR = 1

    def metadata_func_job_descriptions(record: dict, metadata: dict) -> dict:
        metadata["job_id"] = record.get("job_id")
        metadata["title"] = record.get("title")
        metadata["skills"] = record.get("skills", [])
        metadata["experience_level"] = record.get("experience_level")
        metadata["location"] = record.get("location")

        return metadata
    
    def metadata_func_candidate_applications(record: dict, metadata: dict) -> dict:
        metadata["application_id"] = record.get("application_id")
        metadata["job_id"] = record.get("job_id")
        metadata["name"] = record.get("name")
        metadata["email"] = record.get("email")
        metadata["years_experience"] = record.get("years_experience")
        metadata["skills"] = record.get("skills", [])
        metadata["education"] = record.get("education")
        metadata["current_title"] = record.get("current_title")
        metadata["location"] = record.get("location")

        years = record.get("years_experience")
        if isinstance(years, (int, float)):
            if years > 5:
                metadata["experience_level"] = "Senior"
            elif years > 2:
                metadata["experience_level"] = "Mid"
            else:
                metadata["experience_level"] = "Junior"

        

        if record.get("text") and record.get("text") != "":
            score = ScoreCandidates.score(record)
            metadata["score"] = score
            print(f"iteration: {DocumentLoader.ITR}")

            if DocumentLoader.ITR == 10:
                print(f"Iteration {DocumentLoader.ITR}: Sleeping for 80 seconds to avoid rate limits.")
                time.sleep(80)
                DocumentLoader.ITR = 1
            else:    
                DocumentLoader.ITR += 1
        else:
            metadata["score"] = -1

        return metadata


    def load_job_descriptions():

        loader = JSONLoader(
            file_path="jobs/job_descriptions.json",
            jq_schema=".job_descriptions[]",
            content_key="text",
            metadata_func=DocumentLoader.metadata_func_job_descriptions
        )

        docs = loader.load()
        print(f"{len(docs)} docs loaded")
        print(docs[0])

        qdrant = QdrantConfig(collection="job_descriptions").get_vector_store()

        qdrant.add_documents(docs)

    def load_candidate_applications():

        loader = JSONLoader(
            file_path="jobs/candidate_applications.json",
            jq_schema=".applications[]",
            content_key="text",
            metadata_func=DocumentLoader.metadata_func_candidate_applications
        )

        docs = loader.load()
        print(f"{len(docs)} docs loaded")
        print(docs[0])

        qdrant = QdrantConfig(collection="candidate_applications").get_vector_store()
        qdrant.add_documents(docs)
        