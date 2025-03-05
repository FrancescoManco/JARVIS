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
            print("La cartella contiene file o sottocartelle.")
            model_name="llama_finetuning"

        else:
            print("La cartella è vuota o non esiste.")
            model_name ="llama3.2"


        self.llm = ChatOllama(model=model_name, temperature=temperature)
        self.memory = ConversationBufferWindowMemory(k=memory_window_size)  # Short-term memory with a window size

    def execute(self, query: str):
        """
        Execute the query and receive the response.
        """
        # Store the user query in memory
        self.memory.chat_memory.add_user_message(query)

        # Determine the intent of the query
        #intent = self._determine_intent(query)
        personalized_prompt = self.generate_email(query)
        try:


            # Get the response from the LLM model
            response = llama(personalized_prompt)


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

                Generate only the email text body."""
        try:

            #email_content = self.execute(email_generation_prompt)
            #enhanced_prompt = f"{query} Insert the SUBJECT to the email (based on the email body) and use this EMAIL BODY into the 'message' field of the tool.\n\nEmail Body:\n{email_content}"
            #self.memory.chat_memory.add_ai_message(email_content)  # Store the email content in memory
            return email_generation_prompt
        except Exception as e:
            print(f"Error generating email text: {e}")
            return query


# Main Execution
if __name__ == "__main__":
    # Instantiate the workflow with a memory window size of 3
    subj_agent = SubjectiveAgent(memory_window_size=3)
    
    # Example user queries
    user_query1 = "write an email al mio amico domenico roberto e scrivigli che bella giornata"
    response1 = subj_agent.execute(user_query1)
    print(f"Response: {response1}")


