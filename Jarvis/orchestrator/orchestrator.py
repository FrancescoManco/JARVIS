from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END, START
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain.memory import ConversationBufferMemory
from langchain_community.embeddings import HuggingFaceEmbeddings
import faiss
import numpy as np
import json
from datetime import datetime
import os
import operator
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.checkpoint.memory import MemorySaver
from typing import Sequence,Annotated,Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
import sys
import os



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Jarvis.objective.objective import ObjectiveAgent
from Jarvis.subjective.subjectiveModule import SubjectiveAgent
from Jarvis.config import  MONGODB_CONNECTION_STRING, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str




class MultiAgentOrchestrator:
    def __init__(self, model_name: str = "llama3.2"):
        """
        Initialize orchestrator with models and memory systems.
        
        Args:
            model_name: Name of the LLM model to use for supervision
        """

        db_config = {
        "connection_string": MONGODB_CONNECTION_STRING,
        "db_name": MONGODB_DATABASE_NAME,
        "collection_name": MONGODB_COLLECTION_NAME
    }



        
        #self.objective_agent = ChatOllama(model=model_name)
        self.objective_agent = ObjectiveAgent(db_config=db_config)
        self.subjective_agent = SubjectiveAgent(memory_window_size=3)
        self.supervisor_agent = ChatOllama(model=model_name)
        
        self.config = {"configurable": {"thread_id": "1"}}
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the computational graph for multi-agent orchestration."""
        members=["subjective_agent","objective_agent"]
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("subjective_agent", self.subjective_agent_node)
        workflow.add_node("objective_agent", self.objective_agent_node)
        workflow.add_node("supervisor", self.supervisor_node)
        
        #define fixed edges
        workflow.add_edge("subjective_agent","supervisor")
        workflow.add_edge("objective_agent","supervisor")

  ### The supervisor then fills in the 'next' field in the graph state for routing
        conditional_map = {k:k for k in members}
        conditional_map['FINISH'] = END
        workflow.add_conditional_edges(
            "supervisor", lambda x: x['next'],
            conditional_map
        )
        
        ### Connect entrypoint to supervisor
        workflow.add_edge(START, "supervisor")

        ## Add memory - this creates chat history of the graph in an in-memory SQLite database
        memory = MemorySaver()
        
        
        return workflow.compile(checkpointer=memory)
    
    

    def supervisor_node(self, state: AgentState) -> AgentState:
        print("in supervisor node")
        # Preserve the full list of messages
        messages = state['messages']
        print(messages[-1].type)
        last_message_content = messages[-1].content

        print("User message:", last_message_content)
        if not last_message_content:
            raise ValueError("Nessun messaggio utente trovato")
        
        classification_prompt = f"""You are a sophisticated intent classifier.
        Classify the request into ONE of these 3 categories:

        1. objective - If needing external tools/APIs 
        2. subjective - If requiring ONLY personalized text creation ABOUT the user preferences
        3. finish - If THERE ISN'T ANY personal information required and the request is complete

        Clear examples:
        - "Send email to Marco" is objective
        - "Write a poem" is subjective
        - "Hi Jarvis!" is finish
        - "How are you?" is finish
        - "Create a presentation" is subjective
        - "Who is the president in the USA?" is finish

        IMPORTANT: If in the request there is the phrase "send an email" or "send a message" you have to classify it as 'subjective'.
        IMPORTANT: If in the request there is the phrase "SEND TO OBJECTIVE"  you have to classify it as 'objective'.
        IMPORTANT: If in the request there is ANY request about PERSONALIZED TEXT CREATION you have to classify it as 'finish'.
        
        Analyze this request: "{last_message_content}"

        Respond ONLY with one word:
        objective | subjective | finish
        """
        
        decision = self.supervisor_agent.invoke(classification_prompt)
        decision_content = decision.content.strip().lower()

        print("Decision:", decision_content)
        if decision_content == "objective":
            return {"messages": messages, "next": "objective_agent"}
        elif decision_content == "subjective":
            return {"messages": messages, "next": "subjective_agent"}
        elif len(messages) > 1 and messages[-1].type == "ai":

                # Self judgment prompt: evaluate the quality of the last AI response
                judgment_prompt = f"""Analyze the following response: "{messages[-1].content}"
                Evaluate if this response is sufficiently complete and relevant.
                Answer ONLY with 'good' if the response is satisfactory, or 'bad' if it is not."""
                judgment_result = self.supervisor_agent.invoke(judgment_prompt)
                judgment = judgment_result.content.strip().lower()
                print("Judgment:", judgment)
                
                if judgment == "good":
                    # If the answer is good, return it as final
                    return {"messages": messages, "next": "FINISH"}
                elif judgment == "bad":
                    # If the answer is bad, reclassify the user request
                    reclassification_prompt = f"""The previous response was not satisfactory.
                    Reconsider the following user request: "{last_message_content}"
                    Classify the request only as 'objective' or 'subjective'."""
                    reclassification = self.supervisor_agent.invoke(reclassification_prompt)
                    reclassification_decision = reclassification.content.strip().lower()
                    print("Reclassification:", reclassification_decision)
                    if reclassification_decision == "objective":
                        return {"messages": messages, "next": "objective_agent"}
                    elif reclassification_decision == "subjective":
                        return {"messages": messages, "next": "subjective_agent"}
                    else:
                        raise ValueError("Invalid reclassification result")
                else:
                    raise ValueError("Invalid self judgment result")
        else:
            prompt = f"""You are the Supervisor Agent in a multi-agent system. Your task is to DIRECTLY ANSWER requests that don't require tools or personalized generation. The user ask: "{last_message_content}"."""
            
            response = self.supervisor_agent.invoke(prompt)
            new_messages = list(messages)
            new_messages.append(AIMessage(content=response.content.strip()))
            return {"messages": new_messages, "next": "FINISH"}
        
        
    def subjective_agent_node(self, state: AgentState) -> AgentState:
        messages = state['messages']
       
        last_message_content = messages[-1].content
        print("Subjective messages:", last_message_content)
        if not messages:
            raise ValueError("No Message")
        response = self.subjective_agent.execute(last_message_content)
        print("Subjective response:", response)
        new_messages = list(messages)
        new_messages.append(AIMessage(content=response))
        
        return {"messages": new_messages, "next": "supervisor"}
    
    def objective_agent_node(self, state: AgentState) -> AgentState:
        messages = state['messages']
        last_message_content = messages[-1].content
        print("Objective messages:", last_message_content)
        if not messages:
            raise ValueError("No Message")
        response = self.objective_agent.execute(last_message_content)
        print("Objective response:", response)
        new_messages = list(messages)
        new_messages.append(AIMessage(content=response))
        
        return {"messages": new_messages, "next": "supervisor"}

    


    def invoke(self, input_message: str) -> str:
        """Execute the graph with given input."""
        initial_state = {
            "messages": [HumanMessage(content=input_message)],
            "next": "supervisor"
        }
        
        result = self.graph.invoke(initial_state, config=self.config)
        # Estrae l'ultima risposta AI
        for msg in reversed(result['messages']):
            if isinstance(msg, AIMessage):
                return msg.content
        return "Nessuna risposta generata"

    def interactive_chat(self):
        """
        Create an interactive chat interface for the ObjectiveAgent.
        """

        print("🤖 Welcome to JARVIS ")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            try:
                # Get user input
                user_input = input("\n> ")
                
                # Check for exit conditions
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye! Ending conversation.")
                    break
                
                # Execute the query and get response
                response =  self.invoke(user_input)
                
                
                # Print the agent's response
                print("\n🤖 JARVIS:", response)
            
            except KeyboardInterrupt:
                print("\n\nChat interrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"An error occurred: {e}")

    

# Example usage
if __name__ == "__main__":
    orchestrator = MultiAgentOrchestrator()
    orchestrator.interactive_chat()
