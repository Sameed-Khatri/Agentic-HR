from pipeline.load_documents import DocumentLoader

class PipelineRunner:

    def run():
        # DocumentLoader.load_job_descriptions()
        DocumentLoader.load_candidate_applications()
        print("Pipeline run completed successfully.")