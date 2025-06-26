from typing import List, Protocol

from .github import GithubService
from .gitlab import GitlabService

class IRepoService(Protocol): 
    async def get_repo_md_urls(self, repo_url: str) -> List[str]:
        """Get repository markdown URLs."""
        pass

# dictionary to map repo types to their respective tool types
# please note the dict value is a type, not an instance
REPO_SERVICES = dict[str, type(IRepoService)]
services: REPO_SERVICES = {
    "github": GithubService,
    "gitlab": GitlabService
}

async def get_repo_md_urls(repo_url: str) -> List[str]:
    """Get repository markdown URLs.

    Args:
        repo_url: The repository URL.

    Returns:
            Directory of files.
    """
    return await services[_get_repo_type(repo_url)]().get_repo_md_urls(repo_url)

def _get_repo_type(repo_url: str) -> str:
    """Determine the type of repository based on the URL.

    Args:
        repo_url: The repository URL.

    Returns:
        str: The type of repository ('github' or 'gitlab').
    """
    if "github" in repo_url:
        return "github"
    elif "gitlab" in repo_url:
        return "gitlab"
    else:
        raise ValueError("Unsupported repository URL format")

