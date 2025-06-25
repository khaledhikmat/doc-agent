*Initially cloned from: https://github.com/coleam00/ottomator-agents.git. But then I changed it quite a bit*

A documentation crawler and retrieval-augmented generation (RAG) system, powered by Crawl4AI and Pydantic AI. 

The build process (generating the RAG docs) supports reading repo URLs from a URL list separated by a comma. Repo URLs list can be for Gitlab or Github repositories (and they can be mixed). The builder walks through the repository looking for `.md` URLs. The `.md` files content will be source of the documenation knowledge base.

TBA (Mermaid to show how the build and agent run processes work)

---

## Prerequisites

- Python 3.11+
- OpenAI API key (for embeddings and LLM-powered search)
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
- Point to a repository in Github or Gitlab to pull all `.md` file URLs and feed them to the build process.
- Not sure what happens if I re-run build without deleting the `WORKING_DIR`!!!
- Point LightRAG to use Gemini as an option.
