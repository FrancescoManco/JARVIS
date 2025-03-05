# JARVIS

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

JARVIS is an advanced digital agent project based on LLMs (Large Language Models) with a strong focus on adaptive personalization. The goal is to create a system that continuously learns from user input and feedback, improving interaction quality and offering a tailored experience. Through memory modules and fine-tuning techniques, the agent can adapt in real time to the user's preferences and style.
---
# MultiAgentOrchestrator Class Overview

This section describes the core functioning of the **MultiAgentOrchestrator** class. The following points detail the main components:

1. **Initialization (`__init__`)**
2. **Graph Creation (`_create_graph`)**
3. **Supervisor Node (`supervisor_node`)**
6. **Flow Invocation (`invoke`)**

---

## 1. Initialization (`__init__`)

The constructor initializes the orchestrator by setting up the models and memory systems:

- **Database Configuration**: Reads a configuration dictionary containing the MongoDB connection string, database name, and collection name.
- **Agent Initialization**:
  - **Objective Agent**: An instance of `ObjectiveAgent` that handles requests requiring external tools or API interactions.
  - **Subjective Agent**: An instance of `SubjectiveAgent` (using the specified model) for generating personalized responses.
  - **Supervisor Agent**: An instance of `ChatOllama` used to supervise the workflow and route the requests.
- **Graph Setup**: Calls the `_create_graph()` method to construct the computational graph that defines the message flow between the agents.

---

## 2. Graph Creation (`_create_graph`)

This method builds the computational graph that controls the execution flow:

- **Node Definition**: A `StateGraph` is created with three main nodes:
  - `"subjective_agent"` for handling personalized responses.
  - `"objective_agent"` for handling tool/API-based requests.
  - `"supervisor"` for classifying the user request and determining the next step.
- **Edge Configuration**:
  - Fixed edges ensure that both the subjective and objective agents send their output to the supervisor node.
  - The supervisor node uses the `next` field in the state to decide the subsequent agent.
  - The entry point is connected to the supervisor node via the `START` node.
- **Memory Integration**: A memory saver (`MemorySaver`) is attached to maintain the conversation history throughout the session.

---

## 3. Supervisor Node (`supervisor_node`)

This node analyzes the user’s request and routes it appropriately:

- **Message Analysis**: Retrieves and examines the last message sent by the user.
- **Intent Classification**:
  - Sends a prompt to the supervisor agent to classify the request into one of three categories:
    - **objective**: For requests that require the use of external tools or APIs.
    - **subjective**: For requests that require personalized text generation.
    - **finish**: If the request can be answered directly.
- **Routing Decision**:
  - Routes to the **objective agent** if classified as `objective`.
  - Routes to the **subjective agent** if classified as `subjective`.
  - If the conversation already contains an AI response, synthesizes a final answer and ends the flow.

---

## 6. Flow Invocation (`invoke`)

This method executes the computational graph using the user’s input and extracts the final response:

- **Initial State Setup**: Creates an initial state with the user’s message and sets the next node to `supervisor`.
- **Graph Execution**: Invokes the compiled graph with the initial state, processing the request through the defined workflow.
- **Response Extraction**: Iterates over the messages in reverse order to find the last AI-generated message, which is then returned as the final answer.


---
# ObjectiveAgent Functionality Overview

This section describes the core functioning of the **ObjectiveAgent** class, which manages dynamic tool selection and query execution. The following points detail the main components:

1. **Initialization (`__init__`)**
2. **Tool Selection and Classification**
3. **Response Validation (`validate`)**
6. **Query Execution (`execute`)**

---

## 1. Initialization (`__init__`)

- **Tool Setup**:
  - **Gmail Toolkit**: Configures email-related tools by initializing `GmailToolkit` and retrieving the associated tools.
  - **Search Tools**: Initializes search functionality using the Tavily API key and creates separate tools:
    - **Search Tool (`web_search`)**: Performs internet searches via the Tavily API.
    - **Link Tool (`open_link`)**: Opens a specific search result link based on user input.
- **LLM Configuration**: Sets up the language model using `ChatGroq` with the specified model name, temperature, and API key.
- **Tool Registry**: Aggregates all available tools (EMAIL, SEARCH, LINK) into a dictionary for dynamic selection.
- **Memory Database**: Establishes a connection to MongoDB via `MongoDBHandler` to store and manage conversation history.
- **Agent Executor Initialization**: Initializes the agent executor with no tools, to be reconfigured dynamically during query execution.

---

## 2. Tool Selection and Classification

- **Email Tool Classification**:  
  - The `requires_email_tools` method determines if email-related tools are needed by analyzing the user request using keyword matching and an LLM-based prompt.
- **Internet Search Classification**:  
  - The `requires_internet_search` method checks if the request requires an internet search or link handling, leveraging both keyword matching and an LLM prompt.
- **Dynamic Tool Selection**:  
  - The `select_tools` method combines the results from the email and search classifications to select and return the appropriate tools (EMAIL, SEARCH, and/or LINK) from the registry.

---

## 3. Response Validation (`validate`)

- **Purpose**:  
  - Ensures the quality and correctness of the response generated by the agent (**Quality check**).
- **Validation Process**:
  - Constructs a validation prompt to check for clear factual errors, dangerous content, incorrect information, and inappropriate language.
  - Invokes the agent executor with the prompt to receive a validation response.
  - Accepts the response if it returns "VALID"; otherwise, flags it as "INVALID" to trigger a new execution if necessary.

---

## 6. Query Execution (`execute`)

- **Query Processing**:
  - Defines a detailed system prompt that outlines the agent’s objectives, tool usage, and chat history management.
  - Retrieves recent conversation history from MongoDB to provide context.
  - Appends the current user query to the structured message list.
- **Dynamic Tool Integration**:
  - Calls `select_tools` to determine and attach the relevant tools based on the query.
  - Reconfigures the agent executor with the selected tools.
- **Execution and Validation**:
  - Executes the query using the configured LLM and the dynamic set of tools.
  - Validates the raw response using the `validate` method.
  - If the response is valid, it is accepted; otherwise, a new execution is performed.
- **Memory Management**:
  - Stores both the user query and the final validated response in MongoDB to support future context retrieval.


---
# SubjectiveAgent Class Overview

This section provides a brief overview of the **SubjectiveAgent** class, which manages subjective user queries and generates personalized responses.

## 1. Initialization (`__init__`)

- **Model Selection**:  
  - Loads `llama_finetuning` from the `model` directory if available; otherwise, defaults to `llama3.2`.
- **LLM Setup**:  
  - Instantiates the model using `ChatOllama` with a specified temperature.
- **Memory System**:  
  - Initializes a `ConversationBufferWindowMemory` for short-term context storage.

## 2. Intent Classification (`_determine_intent`)

- **Email vs. General Query**:  
  - Use an LLM prompt to classify the request from the user.
  

## 3. Query Execution (`execute`)

- **Processing Steps**:
    - Determines query intent.
    - Execute the query in the correct way based on the intent.
    - Returns the answer from the agent.

## 4. Email Generation (`generate_email`)

- **Prompt Creation**:  
  - Constructs a professional, concise email prompt with a clear subject and message body.

## 5. Data Generation (Dreaming Routine)

This section explains the functionality behind **Dreaming Routing**, a process that generates synthetic email variants using LLM prompts. Although currently tailored for emails, the approach is extendable to other contexts.

## 1. Email Retrieval
- **`get_emails()`**  
  Authenticates using stored credentials, retrieves the last 10 sent emails via the Gmail API, and extracts the text content.  
  If emails are found, it triggers the synthetic email generation process.

## 2. Synthetic Email Generation
- **`email_generation(list_email)`**  
  Processes the list of cleaned emails to generate synthetic variants by:
  - Using a primary prompt (`prompt_email_generation`) to produce a preferred synthetic email.
  - Using an alternative prompt (`prompt_email_generation_non_preferred`) to generate a non-preferred variant.
  - This is done for the DPO Fine Tuning approach.
  
  Generated emails are collected until a target count is reached (e.g., 160), saved into an Excel file.

## Extensibility
The current design is focused on email data, but the underlying methodology can be adapted to other domains. By modifying the prompts and extraction routines, this workflow can generate synthetic data for various content types.
---
## 🔧 SETUP AND CONFIGURATION
@
To set up the system, follow these steps:

### 📌 CONFIGURE `.env` FILE
1. Create a `.env` file in the root directory of the project.
2. Add the following environment variables and fill them with the appropriate values:

    ```env
    TAVILY_API_KEY="your_tavily_api_key"
    GROQ_KEY="your_groq_api_key"
    MONGODB_CONNECTION_STRING="your_mongo_connection_string"
    MONGODB_DATABASE_NAME="your_database_name"
    MONGODB_COLLECTION_NAME="your_collection_name"
    CREDENTIAL_FILE_PATH="Jarvis/objective/credentials.json"
    TOKEN_FILE_PATH="Jarvis/objective/token.json"
    ```:

---

### 🦙 OLLAMA CONFIGURATION
1. Install Ollama via pip:
    ```sh
    pip install ollama
    ```
2. Download the Llama 3.2 (or newer) model via Ollama:
    ```sh
    ollama pull llama3.2
    ```
3. Update the `orchestrator.py` and `subjective.py` files with the downloaded model name (e.g., `"llama3.2"`) inside the `model_name` variable.

---

### ⚡ GROQ CLOUD CONFIGURATION
1. Create an account at [Groq Cloud](https://console.groq.com/login).
2. Generate an API key at [Groq API Keys](https://console.groq.com/keys).
3. Add the API key to the `.env` file as `GROQ_KEY`.

---

### 🔍 TAVILY API CONFIGURATION
1. Create an account at [Tavily](https://tavily.com/).
2. Generate an API key.
3. Add the API key to the `.env` file as `TAVILY_API_KEY`.

---

### 📧 GMAIL TOOLKIT CONFIGURATION
1. Log in to [Google Cloud Console](https://console.cloud.google.com/) with your Google account.
2. Create a new project at [Google Project Creation](https://console.cloud.google.com/projectcreate).
3. Enable the Gmail API at [Google API Library](https://console.cloud.google.com/apis/library).
4. Download the **Credentials JSON File** following the Google API documentation.
5. Save the JSON file as `credentials.json`.
6. Move the JSON file to the `objective` folder.
7. Add the following variables to your `.env` file:

    ```env
    CREDENTIAL_FILE_PATH="Jarvis/objective/credentials.json"
    TOKEN_FILE_PATH="Jarvis/objective/token.json"
    ```

---

### 🗄️ MONGODB CONFIGURATION
1. Download **MongoDB Compass** from [MongoDB Compass Download](https://www.mongodb.com/try/download/compass).
2. Install and open MongoDB Compass.
3. Create a new **DB Connection**.
4. Create a new **Database** inside this connection.
5. Create a new **Collection** inside the database.
6. Add the following variables to your `.env` file:

    ```env
    MONGODB_CONNECTION_STRING="your_connection_string"
    MONGODB_DATABASE_NAME="your_database_name"
    MONGODB_COLLECTION_NAME="your_collection_name"
    ```

---
###  FINETUNING CONFIGURATION
1. insert a base model "llama 3.2" into "Jarvis/subjective/finetuning/base_model" 

## 🚀 RUNNING THE PROJECT
After installing the required dependencies, navigate to the **orchestrator** folder and run:

```sh
python orchestrator.py
```
----

## Project Organization
```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         Jarvis and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── Jarvis   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes Jarvis a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

