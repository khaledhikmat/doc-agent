"""Pydantic AI agent that answers questions about URL-based documentation."""

import os
from dataclasses import dataclass

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from service.rag.typex import IRAGService
from helpers.providers import get_llm_model

# agent dependecies
@dataclass
class DocAgentDeps:
    """Dependencies for the DOC agent."""
    ragsvc: IRAGService

# global variable to hold the agent instance
doc_agent = Agent(
    get_llm_model(), # get the LLM model based on environment variables
    deps_type=DocAgentDeps,
    system_prompt="You are a helpful assistant that answers questions about system documentation based on the provided documentation. "
                    "Use the retrieve tool to get relevant information from the URL documentation before answering. "
                    "If the documentation doesn't contain the answer, clearly state that the information isn't available "
                    "in the current documentation and provide your best general knowledge response."
    )
    
@doc_agent.tool
async def retrieve(context: RunContext[DocAgentDeps], search_query: str) -> str:
    """Retrieve relevant documents from LightRAG based on a search query.
    
    Args:
        context: The run context containing dependencies.
        search_query: The search query to find relevant documents.
        
    Returns:
        Formatted context information from the retrieved documents.
    """
    return await context.deps.ragsvc.retrieve(search_query)
