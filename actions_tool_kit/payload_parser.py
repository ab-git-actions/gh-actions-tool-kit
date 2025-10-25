from .models import WebhookPayload, PayloadRepository, RepoOwner, Sender


def parse_payload(data: dict) -> WebhookPayload:
    """
    Parse a raw GitHub webhook payload dictionary into a strongly typed WebhookPayload object.

    This function extracts structured fields from the incoming event payload such as:
    - `repository`: Includes nested owner data
    - `issue`, `pull_request`, `comment`, `installation`: Passed through as-is if present
    - `sender`: Wrapped into a Sender dataclass
    - `extra`: Any unknown or unmapped fields from the original payload

    Args:
        data (dict): The raw webhook event payload (typically loaded from GITHUB_EVENT_PATH).

    Returns:
        WebhookPayload: A structured representation of the GitHub webhook event,
        with known fields extracted and unknown ones preserved in `extra`.
    """
    # --- Parse repository ---
    repository = data.get("repository")
    if repository:
        owner_data = repository.get("owner", {})
        owner = RepoOwner(
            login=owner_data.get("login", ""),
            name=owner_data.get("name"),
            extra={k: v for k, v in owner_data.items() if k not in {"login", "name"}}
        )
        repo = PayloadRepository(
            name=repository.get("name", ""),
            owner=owner,
            full_name=repository.get("full_name"),
            html_url=repository.get("html_url"),
            extra={k: v for k, v in repository.items() if k not in {"name", "owner", "full_name", "html_url"}}
        )
    else:
        repo = None

    # --- Parse sender ---
    sender_data = data.get("sender")
    sender = None
    if sender_data:
        sender = Sender(
            login=sender_data.get("login", ""),
            type=sender_data.get("type"),
            extra={k: v for k, v in sender_data.items() if k not in {"login", "type"}}
        )

    # --- Construct WebhookPayload ---
    return WebhookPayload(
        repository=repo,
        issue=data.get("issue"),
        pull_request=data.get("pull_request"),
        sender=sender,
        action=data.get("action"),
        installation=data.get("installation"),
        comment=data.get("comment"),
        extra={k: v for k, v in data.items() if k not in {
            "repository", "issue", "pull_request", "sender", "action", "installation", "comment"
        }}
    )
