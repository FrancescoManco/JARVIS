import os
from typing import Any

from langchain.llms.base import LLM
import requests
from langchain_ollama import ChatOllama


def llama(prompt: str) -> Any:
    """
    Initialize the Workflow: with the specified LLM model.
    """
    folder_path = f"Jarvis/subjective/finetuning/model"
    if os.path.exists(folder_path) and os.listdir(folder_path):
        
        model_name = "llama_finetuning"

    else:
       
        model_name = "llama3.2"
    llm = ChatOllama(model=model_name, temperature=0)

    response = llm.invoke(prompt)

    return response


