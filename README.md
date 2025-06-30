*Disclaimer: Picked up code and ideas from: [https://github.com/coleam00/ottomator-agents.git](https://github.com/coleam00/ottomator-agents.git).*

A documentation crawler and retrieval-augmented generation (RAG) system, powered by Crawl4AI and Pydantic AI. 

The build process (generating the RAG docs) supports reading repo URLs from a URL list separated by a comma. Repo URLs list can be for Gitlab or Github repositories (and they can be mixed). The builder walks through the repository looking for `.md` URLs. The `.md` files content will be source of the documenation knowledge base.

TBA (Mermaid to show how the build and agent run processes work)

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

3. **Start Neo4j container:**

- Make sure you have neo4j folder in $HOME.
- Check to make sure that the container is not already running:

```bash
docker ps
```

- Stop the container (optional):

```bash
docker stop neo4j
```

- Remove the container (optional):

```bash
docker rm neo4j
```

- Delete `neo4j` folder subfolders (i.e. `data` and `logs`) and re-create them to remove all data (optional).

- Start the container:

```bash
docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -d \
  -e NEO4J_AUTH="neo4j/admin4neo4j" \
  -v $HOME/neo4j/data:/data \
  -v $HOME/neo4j/logs:/logs \
  neo4j:latest
```

- Access Neo4j dashboard and connect using the credentials provided i.e. `neo4j/admin4neo4j`:

```bash
http://localhost:7474
```

---

## Services

TBA

---

## Pydantic LLM Support

TBA

---

## LightRAG LLM Support

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

## CLI commands

The main entry point for ingesting and vectorizing is [`cli.py`](cli.py). There are different command categories:

### Ingesting into Vectorized Database

```bash
python3 cli.py ingest_lr <repo_url1,repo_url2>
# example:
python3 cli.py ingest_lr https://github.com/khaledhikmat/vs-go
```

Please note there are other ingest commands available to reflect the RAG strategy:
- `ingest_nv`: Naive RAG
- `ingest_lr`: Light RAG
- `ingest_gr`: Graphiti RAG 

### Testing Repo Service

```bash
python3 cli.py test_repo <repo_url>
# example:
python3 cli.py test_repo https://github.com/khaledhikmat/vs-go
```

### Testing Chunker Service

```bash
python3 cli.py test_chunker
```

---

## Running the Agent

After crawling and inserting docs, launch the Streamlit app for semantic search and question answering:

```bash
streamlit run app.py lr
```

- The interface will be available at [http://localhost:8501](http://localhost:8501)
- Query your documentation using natural language and get context-rich answers. Examples:
    - Which language is the the video-sureveillance backend is written in?
    - Can you describe the video-sureveillance architecture?
- The argument `lr` refers to the RAG strategy to use. The following RAG stragtegies are available:
    - `nv`: Naive RAG
    - `lr`: Light RAG
    - `gr`: Graphiti RAG 

---

## Issues

- Although it seems to work ok:
    - I see erros on build that seems to indicate missing packages! It has to do with the `graspologic` package.  
    - I also see some errors like: `limit_async: Critical error in worker: <PriorityQueue at 0x1191c4e10 maxsize=1000> is bound to a different event loop` during querying.
- Not sure what happens if I re-run build without deleting the `WORKING_DIR`!!!
- Add support for multiple RAG strategies
