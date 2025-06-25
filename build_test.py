"""
build_test.py
--------------
Command-line utility to crawl URLs using Crawl4AI and insert into LightRAG.

Usage:
    python3 build_test.py <URLs>
"""
import asyncio
import argparse
from dotenv import load_dotenv

from service.repo.typex import get_repo_md_urls

load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="Test command-line utility to crawl URLs using Crawl4AI and insert into LightRAG.")
    parser.add_argument("repo_urls", help="comma-delimited repo URLs to iterate through looking for .md URLs")
    args = parser.parse_args()

    repo_urls = args.repo_urls.split(',')
    print(f"Received the following repo URLs: {repo_urls}")
    for repo_url in repo_urls:
        urls = await get_repo_md_urls(repo_url.strip())
        if not urls:
            print(f"No markdown URLs found for {repo_url.strip()}")
            continue

        print(f"Will be crawling the following md URLs {urls}...")


if __name__ == "__main__":
    asyncio.run(main())
