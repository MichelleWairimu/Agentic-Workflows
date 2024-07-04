from dotenv import load_dotenv
import os

# Load environment variables from .env file into Python's os.environ
load_dotenv()

# Access your keys
LLAMA_API = os.getenv('LLAMA_API')
LANGSMITH_API = os.getenv('LANGSMITH_API')

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API
os.environ["LANGCHAIN_PROJECT"] = "AGENTIC WORKFLOWS PROJECT"
