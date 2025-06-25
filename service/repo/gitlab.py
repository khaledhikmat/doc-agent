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

        match = re.search(r'gitlab\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', repo_url)
        if not match:
            raise ValueError("Invalid GitLab URL format")
        
        owner, repo = match.groups()
        headers = {'Authorization': f'Bearer {repo_token}'}
        
        response = await http_client.get(
            f'https://gitlab.com/api/v4/projects/{owner}%2F{repo}/repository/tree?recursive=true',
            headers=headers
        )
        
        if response.status_code != 200:
            return f"Failed to get repository structure: {response.text}"
        
        data = response.json()
        structure = []
        for item in data:
            if not any(excluded in item['path'] for excluded in ['.git/', 'node_modules/', '__pycache__/']):
                # structure.append(f"{'📁 ' if item['type'] == 'tree' else '📄 '}{item['path']}")
                if item['path'].endswith('.md'):
                    structure.append(f"{repo_url}/{repo_slug}/{item['path']}")
        
        return structure
