# JARVIS

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

JARVIS is an advanced digital agent project based on LLMs (Large Language Models) with a strong focus on adaptive personalization. The goal is to create a system that continuously learns from user input and feedback, improving interaction quality and offering a tailored experience. Through memory modules and fine-tuning techniques, the agent can adapt in real time to the user's preferences and style.

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
    ```

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

