from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class RepoIdentifier:
    """
    Identifies a GitHub repository by owner and name.

    Attributes:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
    """

    owner: str
    repo: str


@dataclass
class IssueIdentifier:
    """
    Identifies a GitHub issue by repository and issue number.

    Attributes:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        number (int): The issue number.
    """

    owner: str
    repo: str
    number: int


@dataclass
class PullRequestIdentifier:
    """
    Identifies a GitHub pull request by repository and PR number.

    Attributes:
        owner (str): The GitHub username or organization that owns the repository.
        repo (str): The name of the repository.
        number (int): The pull request number.
    """

    owner: str
    repo: str
    number: int


@dataclass
class Sender:
    """
    Represents the user who triggered the GitHub event.

    Attributes:
        login (str): GitHub username of the sender.
        type (Optional[str]): Type of the sender (e.g., 'User', 'Bot', etc.).
        extra (Dict[str, Any]): Any additional fields not explicitly mapped.
    """

    login: str
    type: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RepoOwner:
    """
    Represents the owner of the repository, as part of payload data.

    Attributes:
        login (str): GitHub login of the owner.
        name (Optional[str]): Optional display name of the owner.
        extra (Dict[str, Any]): Additional unmapped fields from the payload.
    """

    login: str
    name: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PayloadRepository:
    """
    Represents the repository object from a GitHub webhook payload.

    Attributes:
        name (str): Name of the repository.
        owner (RepoOwner): The owner object of the repository.
        full_name (Optional[str]): Full name of the repository (e.g., "owner/repo").
        html_url (Optional[str]): URL to the GitHub repository.
        extra (Dict[str, Any]): Any extra unmapped fields in the payload.
    """

    name: str
    owner: RepoOwner
    full_name: Optional[str] = None
    html_url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookPayload:
    """
    Represents the full GitHub webhook event payload.

    Attributes:
        repository (Optional[PayloadRepository]): Repository information from the payload.
        issue (Optional[Dict[str, Any]]): Issue data if the event is related to an issue.
        pull_request (Optional[Dict[str, Any]]): Pull request data if the event is related to a PR.
        sender (Optional[Dict[str, Any]]): User who triggered the event.
        action (Optional[str]): The action type (e.g., "opened", "closed").
        installation (Optional[Dict[str, Any]]): GitHub App installation metadata.
        comment (Optional[Dict[str, Any]]): Comment data if the event involves comments.
        extra (Dict[str, Any]): Any additional unmapped fields from the payload.
    """

    repository: Optional[PayloadRepository] = None
    issue: Optional[Dict[str, Any]] = None
    pull_request: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None
    action: Optional[str] = None
    installation: Optional[Dict[str, Any]] = None
    comment: Optional[Dict[str, Any]] = None
    extra: Dict[str, Any] = field(default_factory=dict)
