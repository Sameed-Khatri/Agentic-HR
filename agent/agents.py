from langgraph.graph import MessagesState
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.messages import AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()


class GloablState(MessagesState):
    query: str
    job_id: str
    job_details: list[dict]
    candidates: list[dict]
    mode: Literal["deepthink", "comparison", "normal", "DONE", "BEGIN"] = Field(default="BEGIN")

class SuperviserOutput(BaseModel):
    action: Literal["deepthink", "comparison", "normal", "DONE"] = Field(description="Action to be taken by the supervisor")

parser = PydanticOutputParser(pydantic_object=SuperviserOutput)

class Models:
    supervisor_model = ChatGroq(model='llama-3.3-70b-versatile', api_key=os.getenv('GROQ_API_KEY'))
    deepthink_model = ChatGroq(model='openai/gpt-oss-120b', api_key=os.getenv('GROQ_API_KEY'))
    comparison_model = ChatGroq(model='openai/gpt-oss-20b', api_key=os.getenv('GROQ_API_KEY'))
    normal_model = ChatGroq(model='llama3-70b-8192', api_key=os.getenv('GROQ_API_KEY'))


class Agents:

    def supervisor(state: GloablState) -> dict:
        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", """You are a supervisor managing a team of agents in the HR department.
                    1. The 'deepthink' agent evaluates candidate applications.
                    2. The 'comparison' agent compares two or more candidates against each other and the job requirements.
                    3. The 'normal' agent answers basic queries related to jobs or candidates, or hiring or any random queries. It can also handle queries asking for a final output or any query that can be answered from the conversation history.

                    Based on the query, assign the task to one of the agents.
                    - Respond with "DONE" if the task is completed.
                    - Respond with "deepthink" to assign to the deepthink agent.
                    - Respond with "comparison" to assign to the comparison agent.
                    - Respond with "normal" to assign to the normal agent.

                    candidates: {candidates}
                    job details: {job_details}
                    
                    Your task is to assign to a delegated agent, you are not allowed to answer user queries yourself.
                    Respond ONLY with a valid JSON object in the following format:
                    {format_instructions}
                    """),
                    MessagesPlaceholder(variable_name="conversation_history"),
                    ("human", "{query}")
                ]
            )

            # pydantic output parser but it fails at times
            # prompt = prompt.partial(format_instructions=parser.get_format_instructions())

            # chain = prompt | Models.supervisor_model | parser

            # custom parsing logic
            chain = prompt | Models.supervisor_model | StrOutputParser()
            
            # output = chain.invoke({'query': state['query'], 'candidates': state['candidates'], 'job_details': state['job_details'], 'conversation_history': state['messages']})

            decision = chain.invoke({'query': state['query'], 'candidates': state['candidates'], 'job_details': state['job_details'], 'conversation_history': state['messages'], 'format_instructions': parser.get_format_instructions()})
            
            if len(decision) > 25:
                raise ValueError("Response is too long or contains unnecessary information.")
            
            # decision = output.action

            print(f"Supervisor Decision Type: {type(decision)}")
            print(f"Supervisor Decision Content: {decision}")
            
            mode = 'DONE'
            if 'deepthink' in decision.lower():
                mode = 'deepthink'
            elif 'comparison' in decision.lower():
                mode = 'comparison'
            elif 'normal' in decision.lower():
                mode = 'normal'
            else:
                raise ValueError("Supervisor was unable to assign this query to an agent.")

            return {'mode': mode, 'messages': [AIMessage(content=decision)]}
        
        except Exception as e:
            # Print the error for debugging purposes
            print(f"Error in supervisor agent: {str(e)}")
            # You can return an error message or a default response
            return {'mode': 'DONE', 'messages': [AIMessage(content="Error processing supervisor task. Agent couldn't answer the query.")]}

    def deepthink(state: GloablState) -> dict:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """you are a in depth analysis agent for HR department.
                Given a query, candidates and job details you will run a detailed analysis on the candidates based on their applications and against the job details.
                Only user information provided, dont add things from your own.
                candidates: {candidates}
                job details: {job_details}"""),
                MessagesPlaceholder(variable_name="conversation_history"),
                ("human", "{query}"),
            ]
        )

        chain = prompt | Models.deepthink_model | StrOutputParser()

        decision = chain.invoke({'query': state['query'], 'candidates': state['candidates'], 'job_details': state['job_details'], 'conversation_history': state['messages']})
        
        print(f"Deepthink Decision Type: {type(decision)}")
        print(f"Deepthink Decision Content: {decision}")

        return {'mode': 'DONE', 'messages': [AIMessage(content=decision)]}
    
    def comparison(state: GloablState) -> dict:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """you are an expert agent in comparing candidate profiles for HR department.
                Given a query, candidates and job details you will compare the candidates with each other and against the job details.
                Only user information provided, dont add things from your own.
                candidates: {candidates}
                job details: {job_details}"""),
                MessagesPlaceholder(variable_name="conversation_history"),
                ("human", "{query}"),
            ]
        )

        chain = prompt | Models.comparison_model | StrOutputParser()

        decision = chain.invoke({'query': state['query'], 'candidates': state['candidates'], 'job_details': state['job_details'], 'conversation_history': state['messages']})
        
        print(f"Comparison Decision Type: {type(decision)}")
        print(f"Comparison Decision Content: {decision}")
        
        return {'mode': 'DONE', 'messages': [AIMessage(content=decision)]}
    
    def normal(state: GloablState) -> dict:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """you are a helpful assistant for HR department.
                Given a query, candidates and job details you will answer the basic queries related to the job or candidates or hiring of basic decision and random queries with access to the conversation history messages.
                Only user information provided, dont add things from your own.
                candidates: {candidates}
                job details: {job_details}"""),
                MessagesPlaceholder(variable_name="conversation_history"),
                ("human", "{query}"),
            ]
        )

        chain = prompt | Models.normal_model | StrOutputParser()

        decision = chain.invoke({'query': state['query'], 'candidates': state['candidates'], 'job_details': state['job_details'], 'conversation_history': state['messages']})

        print(f"Comparison Decision Type: {type(decision)}")
        print(f"Comparison Decision Content: {decision}")

        return {'mode': 'DONE', 'messages': [AIMessage(content=decision)]}
