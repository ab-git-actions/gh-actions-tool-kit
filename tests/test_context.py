import json
import os
import pytest
from pathlib import Path

from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from actions_tool_kit.context import Context


@pytest.fixture
def fake_payload():
    return MagicMock(
        repository=SimpleNamespace(
            name="repo-name",
            owner=SimpleNamespace(login="repo-owner")
        ),
        issue={"number": 123},
        pull_request={"number": 456, "head": {"ref": "feature-branch"}, "base": {"ref": "main"}},
        sender=SimpleNamespace(login="contributor", type="User"),
        extra={"number": 789},
    )


@pytest.fixture
def event_file(tmp_path):
    payload = {
        "repository": {
            "name": "repo-name",
            "owner": {
                "login": "repo-owner"
            }
        },
        "issue": {"number": 123},
        "pull_request": {"number": 456, "head": {"ref": "feature-branch"}, "base": {"ref": "main"}},
        "sender": {"login": "contributor", "type": "User"},
        "extra": {"number": 789}
    }
    file_path = tmp_path / "event.json"
    file_path.write_text(json.dumps(payload))
    return file_path


@patch("actions_tool_kit.context.parse_payload")
def test_context_initialization(mock_parse, event_file, monkeypatch):
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_file))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.setenv("GITHUB_WORKFLOW", "CI")
    monkeypatch.setenv("GITHUB_ACTION", "run")
    monkeypatch.setenv("GITHUB_ACTOR", "octocat")
    monkeypatch.setenv("GITHUB_JOB", "build")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    monkeypatch.setenv("GITHUB_RUN_NUMBER", "45")
    monkeypatch.setenv("GITHUB_RUN_ID", "1001")

    mock_parse.return_value = MagicMock()

    ctx = Context()
    assert ctx.event_name == "push"
    assert ctx.sha == "abc123"
    assert ctx.ref == "refs/heads/main"
    assert ctx.workflow == "CI"
    assert ctx.action == "run"
    assert ctx.actor == "octocat"
    assert ctx.run_attempt == 2
    assert ctx.run_number == 45
    assert ctx.run_id == 1001


@patch("actions_tool_kit.context.parse_payload")
def test_context_repo_env(mock_parse, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "octocat/my-repo")
    mock_parse.return_value = MagicMock(repository=None)

    ctx = Context()
    repo = ctx.repo
    assert repo.owner == "octocat"
    assert repo.repo == "my-repo"


@patch("actions_tool_kit.context.parse_payload")
def test_context_repo_from_payload(mock_parse, monkeypatch):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    payload = MagicMock(
        repository=SimpleNamespace(name="repo-name", owner=SimpleNamespace(login="repo-owner")),
        issue=None,
        pull_request=None,
        sender=None,
        extra={}
    )
    mock_parse.return_value = payload

    ctx = Context()
    repo = ctx.repo
    assert repo.owner == "repo-owner"
    assert repo.repo == "repo-name"


@patch("actions_tool_kit.context.parse_payload")
def test_context_repo_missing(mock_parse, monkeypatch):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    mock_parse.return_value = MagicMock(repository=None)

    ctx = Context()
    with pytest.raises(RuntimeError):
        _ = ctx.repo


@patch("actions_tool_kit.context.parse_payload")
def test_context_issue_and_pr(mock_parse, fake_payload, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "octocat/my-repo")
    mock_parse.return_value = fake_payload
    ctx = Context()

    assert ctx.issue.number == 123
    assert ctx.pr.number == 456


@patch("actions_tool_kit.context.parse_payload")
def test_context_issue_fallback_to_extra(mock_parse, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "octocat/my-repo")
    payload = MagicMock(
        repository=None,
        issue=None,
        pull_request=None,
        sender=None,
        extra={"number": 999}
    )
    mock_parse.return_value = payload
    ctx = Context()

    issue = ctx.issue
    assert issue.number == 999


@patch("actions_tool_kit.context.parse_payload")
def test_context_issue_missing_all(mock_parse, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "octocat/my-repo")
    payload = MagicMock(issue=None, pull_request=None, extra={})
    payload.repository = None
    payload.sender = None
    mock_parse.return_value = payload
    ctx = Context()

    with pytest.raises(RuntimeError):
        _ = ctx.issue


@patch("actions_tool_kit.context.parse_payload")
def test_context_sender_from_payload(mock_parse, fake_payload, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "octocat/my-repo")
    mock_parse.return_value = fake_payload
    ctx = Context()
    assert ctx.sender.login == "contributor"


@patch("actions_tool_kit.context.parse_payload")
def test_context_sender_fallback_to_actor(mock_parse, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTOR", "fallback-user")
    monkeypatch.setenv("GITHUB_REPOSITORY", "octocat/my-repo")
    payload = MagicMock(sender=None, repository=None, issue=None, pull_request=None, extra={})
    mock_parse.return_value = payload

    ctx = Context()
    assert ctx.sender.login == "fallback-user"


@patch("actions_tool_kit.context.parse_payload")
def test_context_branches(mock_parse, fake_payload, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "octocat/my-repo")
    mock_parse.return_value = fake_payload
    ctx = Context()
    assert ctx.head_branch == "feature-branch"
    assert ctx.base_branch == "main"
