import re
import os
import httpx
from typing import List

# this is not nice. Maybe I should send the token as an arg
from dotenv import load_dotenv
load_dotenv()

http_client = httpx.AsyncClient()
repo_token = os.getenv('GITLAB_TOKEN')
repo_slug = os.getenv('GITLAB_SLUG')
gitlab_base_url = os.getenv('GITLAB_BASE_URL', 'https://gitlab.com')

# compliant with RepoService protocol
class GitlabService:
    async def get_repo_md_urls(self, repo_url: str) -> List[str]:
        """
        Get the directory structure of a GitLab repository. 
        and return .md files only

        Args:
            repo_url: The GitLab repository URL.

        Returns:
            Directory of files.
        """
        if not repo_token or not repo_slug:
            raise ValueError("GITLAB_TOKEN and GITLAB_SLUG environment variables must be set")

        match = re.search(r'gitlab\.[^/]+/([^/]+)/([^/]+?)(?:\.git)?$', repo_url)
        if not match:
            raise ValueError("Invalid GitLab URL format")
        
        owner, repo = match.groups()
        headers = {'Authorization': f'Bearer {repo_token}'}
        
        structure = []
        page = 1
        per_page = 100

        while True:
            params = {"recursive": "true", "page": page, "per_page": per_page}
            response = await http_client.get(
                f'{gitlab_base_url}/api/v4/projects/{owner}%2F{repo}/repository/tree',
                headers=headers,
                params=params
            )

            response.raise_for_status()
        
            data = response.json()
            if not data:
                break

            for item in data:
                if item.get('type') == 'blob' and not any(excluded in item['path'] for excluded in ['.git/', 'node_modules/', '__pycache__/']):
                    if item['path'].endswith('.md'):
                        structure.append(f"{repo_url}/{repo_slug}/{item['path']}")

            next_page_header = response.headers.get('x-next-page')
            if next_page_header:
                page = int(next_page_header)
            else:
                break
        
        return structure
