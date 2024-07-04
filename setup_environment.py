import os

LLAMA_API = "LL-8pz7WK0eVmhtkyiHNEDx7vtgq4EeCYCpdOyesCMPvOfTwOiATVVVPKgSbDXFAmfD"
LANGSMITH_API = "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"

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API
os.environ["LANGCHAIN_PROJECT"] = "AGENTIC WORKFLOWS PROJECT"
