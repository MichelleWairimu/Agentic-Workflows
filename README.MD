# Building an Agentic AI Workflow with Llama 3 and LangGraph

This project demonstrates how to build an agentic AI workflow using the Llama 3 open-source LLM model and LangGraph. It creates an autonomous multi-step process that handles a data retrieval task and answers users' questions using multiple specialized AI agents.

## Setup

1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Prepare the database:
    ```sh
    python database_setup.py
    ```

3. Run the main script:
    ```sh
    python main.py
    ```

## Required Libraries

- langchain==0.2.0
- langgraph==0.0.50
- openai==1.30.1
- langchain-openai==0.1.7
