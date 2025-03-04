import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Jarvis.config import GROQ_KEY, TAVILY_API_KEY, MONGODB_CONNECTION_STRING, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME, CREDENTIAL_FILE_PATH, TOKEN_FILE_PATH
import datetime
import json
import re
from typing import  List

from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langchain_groq import ChatGroq
from Jarvis.objective.memory import MongoDBHandler
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from dataclasses import dataclass
from langchain_core.tools import Tool
import webbrowser
from tavily import TavilyClient
import os
# Gmail API Credentials
credentials = get_gmail_credentials(
    token_file=TOKEN_FILE_PATH,  # Path to your token.json
    scopes=["https://mail.google.com/"],  # Gmail scopes
    client_secrets_file=CREDENTIAL_FILE_PATH,  # Path to your credentials.json
)
api_resource = build_resource_service(credentials=credentials)

@dataclass
class SearchResult:
    """Data class to store search results with source information"""
    content: str
    source_url: str
    title: str

class SearchTools:
    """Class to manage search results using Tavily API"""
    def __init__(self, tavily_api_key: str):
        self.client = TavilyClient(api_key=tavily_api_key)
        self.last_search_results: List[SearchResult] = []
    
    def perform_search(self, query: str) -> str:
        """Search tool function using Tavily API"""
        
        try:
            # Perform search with Tavily
            search_response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=3
            )
           
            # Clear previous results
            self.last_search_results.clear()
            
            # Process results
            if search_response["results"] != [] :
                #print("Yes")
                formatted_response = f" Search Results for: '{query}'\n\n"
                
                for i, result in enumerate(search_response['results']):
                    # Store result for link opening
                    self.last_search_results.append(
                        SearchResult(
                            content=result["content"],
                            source_url=result["url"],
                            title=result["title"]
                        )
                    )
                    
                    # Format the result for display
                    formatted_response += f"Result #{i+1}:\n"
                    formatted_response += f" Title: {result.get('title', 'No title available')}\n"
                    formatted_response += f" Content: {result.get('content', 'No content available')}\n"
                    formatted_response += f" Source: {result.get('url', 'No URL available')}\n"
                    formatted_response += f"-------------------------------------------\n\n"
                
                formatted_response += "\nTo open any link, just say 'open link X' where X is the result number."
                print(f"Formatted response: {formatted_response}")
                return formatted_response
            else:
                return "No results found for your search. Please try a different query."
            
        except Exception as e:
            error_msg = str(e)
            print(f"Search error details: {error_msg}")  # For debugging
            return (f"Sorry, I encountered an error while searching. "
                   f"Please try again with a different query.\nError: {error_msg}")
    
   

    def handle_link_opening(self, index: str) -> str:
        """Link opening tool function"""
        try:
            try:
                idx = int(index)
            except ValueError:
                return "⚠️ Please provide a valid number for the link you want to open."
            
            if not self.last_search_results:
                return "⚠️ No recent search results available. Please perform a search first."
            
            if 0 <= idx - 1 < len(self.last_search_results):
                url = self.last_search_results[idx - 1].source_url
                if url:
                    webbrowser.open(url)
                    return f"🔗 Opening link {idx}: {url}"
                else:
                    return "⚠️ Sorry, the URL for this result is not available."
            else:
                return f"⚠️ Invalid link number. Please specify a number between 1 and {len(self.last_search_results)}"
        except Exception as e:
            return f"⚠️ Error opening link: {str(e)}"
        
class ObjectiveAgent:
    """
    A class to manage the objective agent with dynamic tool selection.
    """

    def __init__(self, model_name="llama-3.3-70b-versatile", temperature=0, db_config=None):
            """
            Initialize the Workflow with dynamic tool selection.
            """
            # Add a new attribute to track tool actions
            self.last_tool_action = {
                "executed": False,
                "tool_name": None,
                "result": None
            }

            # Initialize tools
            # Gmail Toolkit Configuration
            self.gmail_toolkit = GmailToolkit(api_resource=api_resource)
            self.gmail_tools = self.gmail_toolkit.get_tools()

            # Initialize search tools with Tavily API key
            tavily_api_key = TAVILY_API_KEY  # Make sure to set this in your environment
            if not tavily_api_key:
                raise ValueError("TAVILY_API_KEY environment variable is not set")
            
            self.search_tools = SearchTools(tavily_api_key)
            
            # Create separate search and link tools
            self.search_tool = Tool(
                name="web_search",
                func=self.search_tools.perform_search,
                description="Search the internet for information using Tavily API. Returns results with numbered sources."
            )
            
            self.link_tool = Tool(
                name="open_link",
                func=self.search_tools.handle_link_opening,
                description="Open a specific search result link in the browser. Input should be the number of the link you want to open (e.g., '1' for the first link)."
            )


            # LLM Configuration
            self.llm = ChatGroq(temperature=temperature, groq_api_key=GROQ_KEY, model_name=model_name)
            
            # Store all possible tools
            self.all_tools = {
                'EMAIL': self.gmail_tools,
                'SEARCH': self.search_tool,
                'LINK': self.link_tool
            }
            
            # MongoDB Configuration
            self.memory_db = MongoDBHandler(
                connection_string=db_config["connection_string"],
                db_name=db_config["db_name"],
                collection_name=db_config["collection_name"]
            )
            
            
            # Initialize agent executor with no tools
            self.agent_executor = create_react_agent(self.llm, [])

    def validate(self, response: str) -> dict:
        """Perform comprehensive validation of the response"""
        print("response:", response)
        try:
            validation_prompt = f"""
            Act as a quality control system. Analyze this response strictly:

            {response}

            Check ONLY for:
            1. Clear factual errors
            2. Dangerous content
            3. Incorrect information
            4. Inappropriate language

            If the task is completed successfully, respond EXACTLY: "VALID"
            If NO issues found, respond EXACTLY: "VALID"
            If ANY issues, respond EXACTLY: "INVALID"
            """

            self.agent_executor = create_react_agent(self.llm, [])

            validation_response = self.agent_executor.invoke(
            {"messages": validation_prompt},
            stream_mode="values",
        )
            print("Validation response:", validation_response["messages"][-1].content)
            if validation_response["messages"][-1].content == "VALID":
                return "VALID"
            else:
                return "INVALID"
        except Exception as e:
            print(f"Validation error: {e}")
            return "INVALID"


        
    def requires_internet_search(self, user_request: str) -> bool:
        """
        Determine if internet search tools are required for the task.
        """
        search_keywords = [
            "search for",
            "look up",
            "find information about",
            "what is",
            "who is",
            "current events",
            "latest news",
            "recent developments",
            "research",
            "define",
            "explain",
            "tell me about",
            "open link"  # Added to catch link opening requests
        ]
        
        # Use LLM for more precise classification
        search_prompt = f"""
        Classify if the following request requires an internet search or link handling:
        Request: "{user_request}"
        
        Respond with:
        - "SEARCH" if the request involves finding information, researching, looking up current details, or opening links
        - "OTHER" for any other type of request
        """
        
        try:
            classification = self.llm.invoke(search_prompt).content.strip().upper()
            
            return classification == "SEARCH"
        except Exception as e:
            print(f"Search tool classification error: {e}")
            
            # Fallback to keyword matching
            return any(keyword in user_request.lower() for keyword in search_keywords)

    def requires_email_tools(self, user_request: str) -> bool:
        """
        Determine if email-related tools are required for the task.
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
        
        # Use LLM for more precise classification
        email_prompt = f"""
        Classify if the following request requires email-related actions:
        Request: "{user_request}"
        
        Respond ONLY with this two options:
        - "EMAIL" if the request involves sending, writing, or managing emails
        - "OTHER" for any other type of request


        """
        
        try:
            classification = self.llm.invoke(email_prompt).content.strip().upper()
            return classification == "EMAIL"
        except Exception as e:
            print(f"Email tool classification error: {e}")
            
            # Fallback to keyword matching
            return any(keyword in user_request.lower() for keyword in email_keywords)

    def select_tools(self, text: str) -> List[Tool]:
        """Dynamically select tools based on the user's request."""
        selected_tools = []
        
        # Check for email tools
        if self.requires_email_tools(text):
            if isinstance(self.all_tools['EMAIL'], list):
                selected_tools.extend(self.all_tools['EMAIL'])
            else:
                selected_tools.append(self.all_tools['EMAIL'])
        
        # Check for search request
        if self.requires_internet_search(text):
            selected_tools.append(self.all_tools['SEARCH'])
        
        # Check for link opening request
        if "open link" in text.lower():
            selected_tools.append(self.all_tools['LINK'])
        
        return selected_tools

    def execute(self, text: str):
        """
        Execute the query with memory included, dynamically selecting tools.
        """
        # Define the system prompt
        system_prompt = """
            You are a highly adaptable and intelligent virtual assistant, designed to help the user with their daily tasks, improve productivity, and provide a personalized experience over time. Your primary objectives are:
            1. Understand and Anticipate User Needs: Learn about the user's preferences, routines, and goals to proactively provide relevant assistance.
            2. Simplify Daily Tasks: Offer solutions, generate ideas, and provide step-by-step guidance for tasks such as planning schedules, managing reminders, composing emails, and searching for information.
            3. Provide Contextually Accurate Information: Answer questions accurately and tailor responses to align with the user's personal context and environment.
            4. Maintain Security and Privacy: Ensure all user data is treated with confidentiality and that personalization enhances the user experience without compromising security.
            5. Communicate Actions Clearly: After performing any action, such as sending an email or conducting a search, inform the user explicitly about what was done and the outcome.
            6. Tool Awareness: You have access to a set of tools to help fulfill user objectives. These tools include:
            - **EMAIL**: For managing email-related tasks like reading, composing, or sending emails.
            - **SEARCH**: For conducting web searches to find relevant and accurate information.
            
            When providing search results, I will include numbered source links. You can ask me to open any link by saying 'open link X' where X is the number of the link you want to open.

            When deciding how to respond, prioritize leveraging these tools when appropriate to ensure efficiency and accuracy. Always explicitly mention which tool you used and why, if applicable.
            Note: When using the search functionality, please be aware that there may be brief delays between searches to avoid rate limiting. If a search is rate-limited, I will inform you and suggest alternative approaches or provide cached results when available.
            Chat History Management:
            - Use the provided chat history to maintain continuity and context. Consider both the user's preferences and prior interactions to enhance your responses.
            - For historical tool calls, summarize key actions and outcomes to provide context for ongoing conversations without overwhelming the user with unnecessary details.
            - Avoid conflating past conversations with the current query but use relevant context from the chat history to ensure consistency and accuracy.
            """

        # Retrieve the chat history from MongoDB
        chat_history = self.get_recent_history()

        #---------------------CHAT HISTORY SETUP---------------------#
        # Format the chat history into a structured message list
        message_list = [{"role": "system", "content": system_prompt}]
        
        # Append historical messages as context without conflating them with the current query
        if chat_history:
            for message in chat_history:
                # Append assistant or user messages
                    message_list.append({
                        "role": message["type"],
                        "content": str(message["content"])
                    })

        #------------------------QUERY SETUP------------------------------------#
        # Add the current user query as the latest message
        message_list.append({"role": "user", "content": text})
        
        #---------------------------------TOOL SETUP--------------------------------------#
        # Select appropriate tools based on the query
        tools = self.select_tools(text)
        if not tools:
            tools = []  # Default to an empty tool list if none are selected

        # Recreate agent executor with selected tools
        self.agent_executor = create_react_agent(self.llm, tools)

        #-------------------------EXECUTE QUERY------------------------------------#
        # Execute the query with the updated agent
        responses = self.agent_executor.invoke(
            {"messages": message_list},
            stream_mode="values",
        )

        #Get raw response
        raw_response = responses["messages"][-1].content
        
        # Perform sanity check with Objective Hemisphere
        validation = self.validate(raw_response)
        
        # Process validation results
        if validation == "VALID":
            final_response = raw_response
        else:
                final_response = self.agent_executor.invoke(
                {"messages": message_list},
                stream_mode="values",
            )
        #--------------------------MEMORY MANAGEMENT------------------------------#
        # Add the current query and response to memory for future context
        self.add_to_memory("user", text)
        self.add_to_memory("ai", final_response)

        return final_response
        #return responses["messages"][-1].content
    
    def add_to_memory(self, message_type: str, content: str):
        """Store a message in MongoDB."""
        message = {
            "type": message_type,
            "content": content,
            "timestamp": datetime.datetime.now()
        }
        self.memory_db.insert_message(message)

    def get_memory_history(self) -> str:
        """Retrieve conversation history from MongoDB."""
        messages = self.memory_db.get_all_messages()
        if not messages:
            return "No conversation history available."
        
        return "\n".join(
            f"{message['type'].capitalize()}: {message['content']}" for message in messages
        )
    
    def get_recent_history(self, max_messages=10):
            """Retrieve the most recent max_messages from memory."""
            messages = self.memory_db.get_all_messages()[-max_messages:]
            return messages

    def clear_memory(self):
        """Clear conversation history in MongoDB."""
        self.memory_db.clear_messages()



def interactive_chat():
    """
    Create an interactive chat interface for the ObjectiveAgent.
    """
    # MongoDB Configuration
    db_config = {
        "connection_string": MONGODB_CONNECTION_STRING,
        "db_name": MONGODB_DATABASE_NAME,
        "collection_name": MONGODB_COLLECTION_NAME
    }

    # Instantiate the agent
    obj_agent = ObjectiveAgent(db_config=db_config)

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
            #response = obj_agent.execute(user_input)
            response = obj_agent.execute(user_input)
            # Print the agent's response
            print("\n🤖 JARVIS:", response)
        
        except KeyboardInterrupt:
            print("\n\nChat interrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    interactive_chat()