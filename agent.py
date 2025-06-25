"""Pydantic AI agent that leverages RAG with a local LightRAG for URL-based documentation."""

import os
import sys
import argparse
import asyncio

import dotenv
from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

from common import WORKING_DIR, RAGDeps

# Load environment variables from .env file
dotenv.load_dotenv()

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete
    )

    await rag.initialize_storages()

    return rag


# Create the URL AI agent
doc_agent = Agent(
    'openai:gpt-4o-mini',
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


def main():
    if not os.path.exists(WORKING_DIR):
        print(f"Error: {WORKING_DIR} must be present and contains RAG docs.")
        sys.exit(1)

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key or set it in your environment.")
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
