import os
from dataclasses import dataclass
from typing import Callable

import numpy as np
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer

from lightrag import LightRAG
from lightrag.llm.openai import openai_complete, gpt_4o_mini_complete, openai_embed
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc

WORKING_DIR = "./url-docs"

@dataclass
class RAGDeps:
    """Dependencies for the RAG agent."""
    lightrag: LightRAG

def get_lightrag_instance(llm_type: str) -> LightRAG:
    """Get the function based on the LLM type."""
    if llm_type not in llm_lightrag_istances:
        raise ValueError(f"Unsupported LLM type: {llm_type}")
    return llm_lightrag_istances[llm_type]() 

# from source code: lightrag -> examples -> lightrag_openai_demo.py
def get_openai_lightrag_instance() -> LightRAG:
    """Get an instance of LightRAG."""
    return LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=openai_complete, # gpt_4o_mini_complete
        llm_model_name=os.getenv("LLM_MODEL"),
    )

# from source code: lightrag -> examples -> lightrag_ollama_demo.py
def get_ollama_lightrag_instance() -> LightRAG:
    """Get an instance of LightRAG."""
    return LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_model_complete,
        llm_model_name=os.getenv("LLM_MODEL", "qwen2.5-coder:7b"),
        llm_model_max_token_size=8192,
        llm_model_kwargs={
            "host": os.getenv("LLM_BINDING_HOST", "http://localhost:11434"),
            "options": {"num_ctx": 8192},
            "timeout": int(os.getenv("TIMEOUT", "300")),
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=int(os.getenv("EMBEDDING_DIM", "1024")),
            max_token_size=int(os.getenv("MAX_EMBED_TOKENS", "8192")),
            func=lambda texts: ollama_embed(
                texts,
                embed_model=os.getenv("EMBEDDING_MODEL", "bge-m3:latest"),
                host=os.getenv("EMBEDDING_BINDING_HOST", "http://localhost:11434"),
            ),
        ),
    )

# from source code: lightrag -> examples -> lightrag_gemini_demo.py
async def gemini_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    # 1. Initialize the GenAI Client with your Gemini API Key
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # 2. Combine prompts: system prompt, history, and user prompt
    if history_messages is None:
        history_messages = []

    combined_prompt = ""
    if system_prompt:
        combined_prompt += f"{system_prompt}\n"

    for msg in history_messages:
        # Each msg is expected to be a dict: {"role": "...", "content": "..."}
        combined_prompt += f"{msg['role']}: {msg['content']}\n"

    # Finally, add the new user prompt
    combined_prompt += f"user: {prompt}"

    # 3. Call the Gemini model
    response = client.models.generate_content(
        model=os.getenv("LLM_MODEL", "gemini-1.5-flash"),
        contents=[combined_prompt],
        config=types.GenerateContentConfig(max_output_tokens=500, temperature=0.1),
    )

    # 4. Return the response text
    return response.text


async def gemini_embedding_func(texts: list[str]) -> np.ndarray:
    model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings

# from source code: lightrag -> examples -> lightrag_gemini_demo.py
def get_gemini_lightrag_instance() -> LightRAG:
    """Get an instance of LightRAG."""
    return  LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gemini_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=384,
            max_token_size=8192,
            func=gemini_embedding_func,
        ),
    )

# dictionary to map llm types to a callable function that returns a LightRAG instance
LLM_LIGHTRAG = dict[str, Callable[..., LightRAG]]
llm_lightrag_istances: LLM_LIGHTRAG = {
    "openai": get_openai_lightrag_instance,
    "gemini": get_gemini_lightrag_instance,
    "ollama": get_ollama_lightrag_instance
}

