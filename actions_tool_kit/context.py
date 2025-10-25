import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from .models import WebhookPayload, RepoIdentifier, IssueIdentifier, PullRequestIdentifier, Sender
from .payload_parser import parse_payload


class Context:
    """
    Context class to access GitHub Actions environment and event payload data.

    Initializes values from environment variables and event JSON payload for ease of access
    to repository, issue, PR, and workflow information inside a GitHub Actions workflow.
    """
    def __init__(self):
        """
        Initialize context by loading event payload and environment variables.
        """
        event_path = os.getenv("GITHUB_EVENT_PATH")
        payload_data = {}

        if event_path:
            path = Path(event_path)
            if path.is_file():
                with open(path, "r", encoding="utf-8") as f:
                    payload_data = json.load(f)
            else:
                print(f"GITHUB_EVENT_PATH {event_path} does not exist\n")

        self.payload: WebhookPayload = parse_payload(payload_data)

        self.event_name = os.getenv("GITHUB_EVENT_NAME")
        self.sha = os.getenv("GITHUB_SHA")
        self.ref = os.getenv("GITHUB_REF")
        self.workflow = os.getenv("GITHUB_WORKFLOW")
        self.action = os.getenv("GITHUB_ACTION")
        self.actor = os.getenv("GITHUB_ACTOR")
        self.job = os.getenv("GITHUB_JOB")
        self.run_attempt = int(os.getenv("GITHUB_RUN_ATTEMPT", "0"))
        self.run_number = int(os.getenv("GITHUB_RUN_NUMBER", "0"))
        self.run_id = int(os.getenv("GITHUB_RUN_ID", "0"))
        self.api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")
        self.server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
        self.graphql_url = os.getenv("GITHUB_GRAPHQL_URL", "https://api.github.com/graphql")

    @property
    def repo(self) -> RepoIdentifier:
        """
        Get repository identifier from environment or payload.

        Returns:
            RepoIdentifier: Object containing `owner` and `repo` name.

        Raises:
            RuntimeError: If repository information is unavailable.
        """
        repo_str = os.getenv("GITHUB_REPOSITORY")

        if repo_str:
            owner, repo = repo_str.split("/")
            return RepoIdentifier(owner=owner, repo=repo)

        if self.payload.repository:
            return RepoIdentifier(
                owner=self.payload.repository.owner.login,
                repo=self.payload.repository.name
            )

        raise RuntimeError("context.repo requires a GITHUB_REPOSITORY environment variable like 'owner/repo'")

    @property
    def issue(self) -> IssueIdentifier:
        """
        Get issue identifier from payload. Falls back to pull request number if no issue is present.

        Returns:
            IssueIdentifier: Object containing `owner`, `repo`, and `number`.

        Raises:
            RuntimeError: If issue number is unavailable.
        """
        if self.payload.issue and "number" in self.payload.issue:
            number = self.payload.issue["number"]
        elif self.payload.pull_request and "number" in self.payload.pull_request:
            number = self.payload.pull_request["number"]
        else:
            number = self.payload.extra.get("number")

        if number is None:
            raise RuntimeError("context.issue is not available for this event type")

        return IssueIdentifier(
            owner=self.repo.owner,
            repo=self.repo.repo,
            number=number,
        )

    @property
    def pr(self) -> Optional[PullRequestIdentifier]:
        """
        Get pull request identifier from payload.

        Returns:
            PullRequestIdentifier | None: PR identifier if present, else None.
        """
        if self.payload.pull_request and "number" in self.payload.pull_request:
            return PullRequestIdentifier(
                owner=self.repo.owner,
                repo=self.repo.repo,
                number=self.payload.pull_request["number"]
            )
        return None

    @property
    def sender(self) -> dict[str, Any] | Sender:
        """
        Get sender information from payload or fallback to actor environment variable.

        Returns:
            Sender | dict: Sender object if available, otherwise fallback dict with login.
        """
        if self.payload.sender:
            return self.payload.sender
        return Sender(login=self.actor, type=None)

    @property
    def head_branch(self) -> Optional[str]:
        """
        Get the source branch of a pull request.

        Returns:
            str | None: Head branch name or None if not a PR.
        """
        if self.payload.pull_request:
            return self.payload.pull_request.get("head", {}).get("ref")
        return None

    @property
    def base_branch(self) -> Optional[str]:
        """
        Get the target branch of a pull request.

        Returns:
            str | None: Base branch name or None if not a PR.
        """
        if self.payload.pull_request:
            return self.payload.pull_request.get("base", {}).get("ref")
        return None


# Instance of context for easy reuse
context = Context()
