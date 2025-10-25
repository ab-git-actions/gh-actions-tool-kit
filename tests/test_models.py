import pytest
from actions_tool_kit.models import (
    RepoIdentifier,
    IssueIdentifier,
    PullRequestIdentifier,
    Sender,
    RepoOwner,
    PayloadRepository,
    WebhookPayload,
)


def test_repo_identifier():
    repo = RepoIdentifier(owner="octocat", repo="hello-world")
    assert repo.owner == "octocat"
    assert repo.repo == "hello-world"


def test_issue_identifier():
    issue = IssueIdentifier(owner="octocat", repo="hello-world", number=42)
    assert issue.owner == "octocat"
    assert issue.repo == "hello-world"
    assert issue.number == 42


def test_pull_request_identifier():
    pr = PullRequestIdentifier(owner="octocat", repo="hello-world", number=99)
    assert pr.owner == "octocat"
    assert pr.repo == "hello-world"
    assert pr.number == 99


def test_sender_with_extra():
    sender = Sender(login="octocat", type="User", extra={"id": 1, "site_admin": False})
    assert sender.login == "octocat"
    assert sender.type == "User"
    assert sender.extra["id"] == 1
    assert sender.extra["site_admin"] is False


def test_sender_without_extra():
    sender = Sender(login="bot-account")
    assert sender.login == "bot-account"
    assert sender.type is None
    assert sender.extra == {}


def test_repo_owner_with_extra():
    owner = RepoOwner(login="octocat", name="The Octocat", extra={"id": 123})
    assert owner.login == "octocat"
    assert owner.name == "The Octocat"
    assert owner.extra == {"id": 123}


def test_repo_owner_without_extra():
    owner = RepoOwner(login="octocat")
    assert owner.name is None
    assert owner.extra == {}


def test_payload_repository_minimal():
    owner = RepoOwner(login="octocat")
    repo = PayloadRepository(name="hello-world", owner=owner)
    assert repo.name == "hello-world"
    assert repo.owner.login == "octocat"
    assert repo.full_name is None
    assert repo.html_url is None
    assert repo.extra == {}


def test_payload_repository_with_extra():
    owner = RepoOwner(login="octocat", name="The Octocat")
    repo = PayloadRepository(
        name="hello-world",
        owner=owner,
        full_name="octocat/hello-world",
        html_url="https://github.com/octocat/hello-world",
        extra={"private": False}
    )
    assert repo.full_name == "octocat/hello-world"
    assert repo.html_url == "https://github.com/octocat/hello-world"
    assert repo.extra["private"] is False


def test_webhook_payload_defaults():
    payload = WebhookPayload()
    assert payload.repository is None
    assert payload.issue is None
    assert payload.pull_request is None
    assert payload.sender is None
    assert payload.action is None
    assert payload.installation is None
    assert payload.comment is None
    assert payload.extra == {}


def test_webhook_payload_with_fields():
    repo_owner = RepoOwner(login="octocat", name="The Octocat")
    payload_repo = PayloadRepository(name="repo", owner=repo_owner)

    payload = WebhookPayload(
        repository=payload_repo,
        issue={"number": 1},
        pull_request={"number": 2},
        sender={"login": "octocat"},
        action="opened",
        installation={"id": 123},
        comment={"body": "Looks good"},
        extra={"custom": "value"}
    )

    assert payload.repository.name == "repo"
    assert payload.issue["number"] == 1
    assert payload.pull_request["number"] == 2
    assert payload.sender["login"] == "octocat"
    assert payload.action == "opened"
    assert payload.installation["id"] == 123
    assert payload.comment["body"] == "Looks good"
    assert payload.extra["custom"] == "value"
