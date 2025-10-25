import pytest
from actions_tool_kit.models import WebhookPayload, PayloadRepository, RepoOwner, Sender
from actions_tool_kit.payload_parser import parse_payload


def test_parse_payload_full():
    payload_dict = {
        "repository": {
            "name": "my-repo",
            "full_name": "owner/my-repo",
            "html_url": "https://github.com/owner/my-repo",
            "owner": {
                "login": "owner",
                "name": "Repo Owner",
                "avatar_url": "https://avatars.githubusercontent.com/u/1"
            },
            "private": True
        },
        "issue": {"number": 123},
        "pull_request": {"number": 456},
        "sender": {
            "login": "octocat",
            "type": "User",
            "id": 999
        },
        "action": "opened",
        "installation": {"id": 42},
        "comment": {"body": "Looks good"},
        "custom_field": "value"
    }

    result: WebhookPayload = parse_payload(payload_dict)

    # Check repository
    assert isinstance(result.repository, PayloadRepository)
    assert result.repository.name == "my-repo"
    assert result.repository.full_name == "owner/my-repo"
    assert result.repository.owner.login == "owner"
    assert result.repository.owner.name == "Repo Owner"
    assert result.repository.owner.extra["avatar_url"] == "https://avatars.githubusercontent.com/u/1"
    assert result.repository.extra["private"] is True

    # Check sender
    assert isinstance(result.sender, Sender)
    assert result.sender.login == "octocat"
    assert result.sender.type == "User"
    assert result.sender.extra["id"] == 999

    # Check issue and PR
    assert result.issue["number"] == 123
    assert result.pull_request["number"] == 456

    # Check other fields
    assert result.action == "opened"
    assert result.installation["id"] == 42
    assert result.comment["body"] == "Looks good"
    assert result.extra["custom_field"] == "value"


def test_parse_payload_missing_repository_and_sender():
    data = {
        "issue": {"number": 789},
        "pull_request": {"number": 555},
        "action": "closed",
        "comment": {"body": "done"},
        "custom_thing": 123
    }

    result = parse_payload(data)

    assert result.repository is None
    assert result.sender is None
    assert result.issue["number"] == 789
    assert result.pull_request["number"] == 555
    assert result.action == "closed"
    assert result.comment["body"] == "done"
    assert result.extra == {"custom_thing": 123}


def test_parse_payload_minimal():
    result = parse_payload({})
    assert isinstance(result, WebhookPayload)
    assert result.repository is None
    assert result.sender is None
    assert result.issue is None
    assert result.extra == {}


def test_parse_payload_partial_owner_data():
    data = {
        "repository": {
            "name": "demo",
            "owner": {
                "login": "demo-user"
                # no name or extras
            }
        }
    }

    result = parse_payload(data)

    assert result.repository.name == "demo"
    assert result.repository.owner.login == "demo-user"
    assert result.repository.owner.name is None
    assert result.repository.owner.extra == {}
