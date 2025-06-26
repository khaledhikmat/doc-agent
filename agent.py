"""Pydantic AI agent that leverages RAG with a local LightRAG for URL-based documentation."""

import os
import sys
import argparse
import asyncio

import dotenv
from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from lightrag import QueryParam

from common import WORKING_DIR, RAGDeps, get_lightrag_instance

# Load environment variables from .env file
dotenv.load_dotenv()

# dictionary to map llm types to model name to be used with Pydantic AI agents
llm_agent_names: dict[str, str] = {
    "openai": f"openai:{os.getenv('LLM_MODEL', 'gpt-4o-mini')}",
    "gemini": f"google-gla:{os.getenv('LLM_MODEL', 'gemini-2.0-flash')}",
    "ollama": "not-supported-yet"
}

# Create the doc AI agent
doc_agent = Agent(
    llm_agent_names[os.getenv("LLM_TYPE", "openai")],
    deps_type=RAGDeps,
    system_prompt="You are a helpful assistant that answers questions about system documentation based on the provided documentation. "
                  "Use the retrieve tool to get relevant information from the URL documentation before answering. "
                  "If the documentation doesn't contain the answer, clearly state that the information isn't available "
                  "in the current documentation and provide your best general knowledge response."
)

@doc_agent.tool
async def retrieve(context: RunContext[RAGDeps], search_query: str) -> str:
    """Retrieve relevant documents from LightRAG based on a search query.
    
    Args:
        context: The run context containing dependencies.
        search_query: The search query to find relevant documents.
        
    Returns:
        Formatted context information from the retrieved documents.
    """
    return await context.deps.lightrag.aquery(
        search_query, param=QueryParam(mode="mix")
    )

async def run_rag_agent(question: str,) -> str:
    """Run the RAG agent to answer a question about URL documentation.
    
    Args:
        question: The question to answer.
        
    Returns:
        The agent's response.
    """
    # Create dependencies
    lightrag = await initialize_rag()
    deps = RAGDeps(lightrag=lightrag)
    
    # Run the agent
    result = await doc_agent.run(question, deps=deps)
    
    return result.data

async def initialize_rag():
    rag = get_lightrag_instance(os.getenv("LLM_TYPE"))
    await rag.initialize_storages()
    return rag

def main():
    if not os.path.exists(WORKING_DIR):
        print(f"Error: {WORKING_DIR} must be present and contains RAG docs.")
        sys.exit(1)

    if not os.getenv("LLM_TYPE") or os.getenv("LLM_TYPE") not in ["openai", "gemini", "ollama"]:
        print("Error: LLM_TYPE environment variable not set or invalid.")
        print("Please create a .env file with LLM_TYPE set to 'openai', 'gemini', or 'ollama'.")
        sys.exit(1)

    if not os.getenv("LLM_MODEL"):
        print("Error: LLM_MODEL environment variable must be set.")
        print("Please create a .env file with your LLM model name or set it in your environment.")
        sys.exit(1)

    # Check for OpenAI API key
    if os.getenv("LLM_TYPE") == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key or set it in your environment.")
        sys.exit(1)

    # Check for OpenAI API key
    if os.getenv("LLM_TYPE") == "gemini" and not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please create a .env file with your Gemini API key or set it in your environment.")
        sys.exit(1)

    """Main function to parse arguments and run the RAG agent."""
    parser = argparse.ArgumentParser(description="Run a URL agent with RAG using LightRAG")
    parser.add_argument("--question", help="The question to answer about URL documentation", required=True)
    
    args = parser.parse_args()
    
    # Run the agent
    response = asyncio.run(run_rag_agent(args.question))
    
    print("\nResponse:")
    print(response)


if __name__ == "__main__":
    main()
