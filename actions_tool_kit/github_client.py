from github import Github
from typing import Optional, Dict, Any

from pycparser.ply.yacc import token


def get_github_client(token: str, **options: Any) -> Github:
    """
    Returns an authenticated GitHub client using PyGithub.

    Required:
        - token: GitHub token (PAT or GitHub Actions token)

    Optional keyword arguments:
        - base_url: str
        - timeout: int
        - user_agent: str
        - per_page: int
        - verify: bool | str
        - retry: int | Retry
        - pool_size: int
        - seconds_between_requests: float
        - seconds_between_writes: float
        - auth: GitHub.Auth.Auth
        - jwt: str
        - password: str
        - app_auth: AppAuthentication
        - lazy: bool
    """
    return Github(login_or_token=token, **options)
