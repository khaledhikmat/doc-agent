"""
build.py
--------------
Command-line utility to crawl URLs using Crawl4AI and insert into LightRAG.

Usage:
    python3 build.py <URLs>
"""
import os
import sys
import asyncio
from urllib.parse import urldefrag
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv
from lightrag.kg.shared_storage import initialize_pipeline_status
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher

from common import WORKING_DIR, get_lightrag_instance
from service.repo.typex import get_repo_md_urls

load_dotenv()

async def crawl_recursive_internal_links(start_urls, max_depth=3, max_concurrent=10) -> List[Dict[str,Any]]:
    """Returns list of dicts with url and markdown."""
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent
    )

    visited = set()

    def normalize_url(url):
        return urldefrag(url)[0]

    current_urls = set([normalize_url(u) for u in start_urls])
    results_all = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for depth in range(max_depth):
            urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]
            if not urls_to_crawl:
                break

            results = await crawler.arun_many(urls=urls_to_crawl, config=run_config, dispatcher=dispatcher)
            next_level_urls = set()

            for result in results:
                norm_url = normalize_url(result.url)
                visited.add(norm_url)

                if result.success and result.markdown:
                    results_all.append({'url': result.url, 'markdown': result.markdown})
                    for link in result.links.get("internal", []):
                        next_url = normalize_url(link["href"])
                        if next_url not in visited:
                            next_level_urls.add(next_url)

            current_urls = next_level_urls

    return results_all

async def initialize_rag():
    rag = get_lightrag_instance(os.getenv("LLM_TYPE"))
    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

async def main():
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

    # Check if WORKING_DIR exists, delete and recreate it
    if os.path.exists(WORKING_DIR):
        import shutil
        shutil.rmtree(WORKING_DIR)
    os.mkdir(WORKING_DIR)
    
    crawl_results = []

    parser = argparse.ArgumentParser(description="Insert crawled docs into LightRAG")
    parser.add_argument("repo_urls", help="comma-delimited repo URLs to iterate through looking for .md URLs")
    args = parser.parse_args()

    repo_urls = args.repo_urls.split(',')
    print(f"Received the following repo URLs: {repo_urls}")
    for repo_url in repo_urls:
        urls = await get_repo_md_urls(repo_url.strip())
        if not urls:
            print(f"No markdown URLs found for {repo_url.strip()}")
            continue

        print(f"Crawling the following md URLs {urls}...")
        crawl_results.extend(await crawl_recursive_internal_links(urls, max_depth=1, max_concurrent=10))

    # Initialize RAG instance and insert docs
    rag = await initialize_rag()
    for doc in crawl_results:
        url = doc['url']
        md = doc['markdown']
        if not md:
            print(f"Skipping {url} - no markdown content found")
            continue
        print(f"Inserting document from {url} into RAG...")
        await rag.ainsert(md)

if __name__ == "__main__":
    asyncio.run(main())
    print(f"Successfully added docs to vector database using RAGLight.")
