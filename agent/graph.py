from agent.agents import Agents, GloablState
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from typing import Literal

class Graph:
    checkpointer = InMemorySaver()

    def supervisor_decision(state: GloablState) -> Literal["deepthink", "comparison", "normal", "END"]:
        if state['mode'] == 'deepthink':
            return 'deepthink'
        elif state['mode'] == 'comparison':
            return 'comparison'
        elif state['mode'] == 'normal':
            return 'normal'
        else:
            return 'END'


    graph = StateGraph(GloablState)

    graph.add_node('supervisor', Agents.supervisor)
    graph.add_node('deepthink', Agents.deepthink)
    graph.add_node('comparison', Agents.comparison)
    graph.add_node('normal', Agents.normal)

    graph.add_edge(START, 'supervisor')
    graph.add_conditional_edges(
        'supervisor',
        supervisor_decision,
        {
            'deepthink': 'deepthink',
            'comparison': 'comparison',
            'normal': 'normal',
            'END': END
        }
    )
    # graph.add_edge('deepthink', 'supervisor')
    # graph.add_edge('comparison', 'supervisor')
    # graph.add_edge('normal', 'supervisor')

    graph.add_edge('deepthink', END)
    graph.add_edge('comparison', END)
    graph.add_edge('normal', END)

    agents = graph.compile(checkpointer=checkpointer)


    def invoke_agents(state: dict, thread_id: str):
        config = {
            'configurable': {
                'thread_id': thread_id
            }
        }

        if 'messages' not in state:
            state['messages'] = [HumanMessage(content=state.get('query'))]

        response = Graph.agents.invoke(state, config=config)

        # print(list(Graph.agents.get_state_history(config=config)))

        return response