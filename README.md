*Initially cloned from: https://github.com/coleam00/ottomator-agents.git. But then I changed it quite a bit*

A documentation crawler and retrieval-augmented generation (RAG) system, powered by Crawl4AI and Pydantic AI. 

The build process (generating the RAG docs) supports reading repo URLs from a URL list separated by a comma. Repo URLs list can be for Gitlab or Github repositories (and they can be mixed). The builder walks through the repository looking for `.md` URLs. The `.md` files content will be source of the documenation knowledge base.

TBA (Mermaid to show how the build and agent run processes work)

---

## LLM Support

Normally, LightRAG works out of the box with OpenAI and it seems it is a good option. But if you don't want to use OpenAI or any other Cloud-based models, the other option is to use Ollama as it has out-of-the-box support in LightRAG. This project supports `openai`, `gemini` and `ollama`. 

Please note that the `Gemini` support is not totally native. I noticed a huge performance degredation when using Gemini. Defintely the best option is OpenAI.

To activate OpenAI, please set the following env vars:
- `LLM_TYPE=openai`
- `LLM_MODEL_NAME=gpt-4o-mini`
- `OPENAI_API_KEY=<openai-api-key>`

To activate Gemini, please set the following env vars:
- `LLM_TYPE=gemini`
- `LLM_MODEL_NAME=gemini-1.5-flash`
- `GEMINI_API_KEY=<gemini-api-key>`

To activate Ollama, please set the following env vars:
- `LLM_TYPE=ollama`
- `LLM_MODEL_NAME=qwen2.5-coder:7b`

**Please note** if you are running Ollama, you must download and install Ollam locally and then run it:
- On Unix:
    - `curl -fsSL https://ollama.com/install.sh | sh`
- On MacOS & Windows:
    - Visit https://ollama.com/download
- `ollama pull qwen2.5-coder:7b`
- `ollama pull bge-m3:latest`
- `ollama serve` # On Mac OS, the agent starts automatically
- To confirm models are pulled properly, open up a new terminal and do: `ollama list`.
- To confirm Ollama is running: `curl http://localhost:11434/api/tags`
- Ollama runs the models locally and hence it requires a lot of processing power. I was not able to make it work well. My Mac (16 GB) was heating up quite a bit.

---

## Prerequisites

- Python 3.11+
- OpenAI API key (for embeddings and LLM-powered search)
- GeminiAI API key (for LLM-powered search)
- Dependencies in `requirements.txt`

---

## Installation

1. **Install dependencies:**

```bash
python3 -m venv venv
source venv/bin/activate 
pip3 install -r requirements.txt
playwright install
```

2. **Set up environment variables:**

- Copy `.env.example` to `.env`
- Edit `.env` with your API keys and preferences.

---

## Testing Repo URLs

The main entry point for testing `.md` files retrieval is [`build_test.py`](build_test.py):

```bash
python3 build_test.py <repo_url1,repo_url2>
# example:
python3 build_test.py https://github.com/khaledhikmat/vs-go
```

---

## Building Vectorized Database

The main entry point for crawling and vectorizing documentation is [`build.py`](build.py):

```bash
python3 build.py <repo_url1,repo_url2>
# example:
python3 build.py https://github.com/khaledhikmat/vs-go
```

---

## Running the Agent

After crawling and inserting docs, launch the Streamlit app for semantic search and question answering:

```bash
streamlit run app.py
```

- The interface will be available at [http://localhost:8501](http://localhost:8501)
- Query your documentation using natural language and get context-rich answers. Examples:
    - Which language is the the video-sureveillance backend is written in?
    - Can you describe the video-sureveillance architecture?

---

## Issues

- Although it seems to work ok:
    - I see erros on build that seems to indicate missing packages! It has to do with the `graspologic` package.  
    - I also see some errors like: `limit_async: Critical error in worker: <PriorityQueue at 0x1191c4e10 maxsize=1000> is bound to a different event loop` during querying.
- Not sure what happens if I re-run build without deleting the `WORKING_DIR`!!!
