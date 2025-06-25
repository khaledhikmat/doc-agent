from dataclasses import dataclass

from lightrag import LightRAG

WORKING_DIR = "./url-docs"

@dataclass
class RAGDeps:
    """Dependencies for the RAG agent."""
    lightrag: LightRAG
