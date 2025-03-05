import os
import time

from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferWindowMemory

from Jarvis.subjective.inferenza import fine_tuned_response
from Jarvis.utils.Ollama import llama


class SubjectiveAgent:
    """
    A class to manage the subjective agent.
    """

    def __init__(self, model_name="llama3.2", temperature=0, memory_window_size=3):
        """
        Initialize the Workflow with the specified LLM model and memory.
        """
        folder_path =  f"model"
        if os.path.exists(folder_path) and os.listdir(folder_path):
            print("No File in the Directory")
            model_name="llama_finetuning"

        else:
            print("Empty folder.")
            model_name ="llama3.2"


        self.llm = ChatOllama(model=model_name, temperature=temperature)
        self.memory = ConversationBufferWindowMemory(k=memory_window_size)  # Short-term memory with a window size


    def _determine_intent(self, query: str) -> str:
        """
        Determine the intent of the query.
        """
        email_keywords = [
            "send email", 
            "write email", 
            "compose email", 
            "email to", 
            "draft email", 
            "send a message",
            "compose message",
            "write to"
        ]
        email_prompt = f"""
        Classify if the following request is related to an email action:
        Request: "{query}"
        
        Respond ONLY with these two options:
        - "EMAIL" if the request involves sending, writing, or managing emails
        - "OTHER" for any other type of request
        """
        try:
            classification = self.llm.invoke(email_prompt).content.strip().upper()
            print("subjective classification: ", classification)
            return classification 
        except Exception as e:
            print(f"Email tool classification error: {e}")
            return "EMAIL" if any(keyword in query.lower() for keyword in email_keywords) else "OTHER"
        
    def execute(self, query: str):
        """
        Execute the query and receive the response.
        """
        # Store the user query in memory
        self.memory.chat_memory.add_user_message(query)

        # Determine the intent of the query
        intent = self._determine_intent(query)

        if intent == "EMAIL":
            personalized_prompt = self.generate_email(query)
            print("Personalized Prompt: ", personalized_prompt)
            try:


                # Get the response from the LLM model
                response = llama(personalized_prompt)
                

                # Store the LLM response in memory
                self.memory.chat_memory.add_ai_message(response)
                #print(response.content)

                final_response = f""" {query} with this text body: {response.content}. SEND TO OBJECTIVE"""
                print("Response in email gen: ", final_response)
                return final_response
            except Exception as e:
                print(f"Error invoking LLM: {str(e)}")
                return f"Error processing request: {str(e)}"
        else:
            
            try:


                # Get the response from the LLM model
                response = llama(query)
                print("Response: ", response.content)

                # Store the LLM response in memory
                self.memory.chat_memory.add_ai_message(response)
                #print(response.content)

                return response.content
            except Exception as e:
                print(f"Error invoking LLM: {str(e)}")
                return f"Error processing request: {str(e)}"




    def generate_email(self, query: str) -> str:
        """
        Generate an email text and concatenate it to the original query.
        """
        email_generation_prompt = f"""
                You are a professional email composer. Based on the following request, generate a concise and professional email text:
                Request: "{query}"

                Guidelines for email generation:
                1. Keep the tone professional and courteous
                2. Clearly state the purpose of the email
                4. Include necessary details
                5. Use a standard email format
                
                Insert the SUBJECT to the email (based on the email body) and use this EMAIL BODY into the 'message' field of the tool.

                Generate only the email text body.
                               
                """
        try:

           
            return email_generation_prompt
        except Exception as e:
            print(f"Error generating email text: {e}")
            return query


