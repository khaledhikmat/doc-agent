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
import dotenv
from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher

from common import WORKING_DIR

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
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

def main():
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key or set it in your environment.")
        sys.exit(1)

    # Check if WORKING_DIR exists, delete and recreate it
    if os.path.exists(WORKING_DIR):
        import shutil
        shutil.rmtree(WORKING_DIR)
    os.mkdir(WORKING_DIR)
    
    parser = argparse.ArgumentParser(description="Insert crawled docs into LightRAG")
    parser.add_argument("urls", help="comma-delimited URLs to crawl (.md)")
    args = parser.parse_args()

    # Detect URL type
    urls = args.urls.split(',')
    print(f"Detected regular URL: {urls}")
    crawl_results = asyncio.run(crawl_recursive_internal_links(urls, max_depth=1, max_concurrent=10))

    # Initialize RAG instance and insert docs
    rag = asyncio.run(initialize_rag())
    for doc in crawl_results:
        url = doc['url']
        md = doc['markdown']
        if not md:
            print(f"Skipping {url} - no markdown content found")
            continue
        print(f"Inserting document from {url} into RAG...")
        rag.insert(md)

if __name__ == "__main__":
    main()
    print(f"Successfully added docs to RAGLight.")
