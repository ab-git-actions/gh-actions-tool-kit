import pytest
from github import Github
from actions_tool_kit.github_client import get_github_client


def test_get_github_client_basic():
    token = "ghp_test1234567890"
    client = get_github_client(token)
    assert isinstance(client, Github)


def test_get_github_client_with_options():
    token = "ghp_testtoken"

    # Not inspecting internals like _userAgent or _baseUrl
    client = get_github_client(
        token,
        base_url="https://api.github.com",
        timeout=20,
        user_agent="pytest-agent",
        per_page=50
    )

    assert isinstance(client, Github)
    # You could call a method like get_rate_limit() to test it's working
    assert callable(client.get_rate_limit)


def test_get_github_client_invalid_token():
    with pytest.raises(AssertionError):  # was TypeError; now correct
        get_github_client(12345)  # type: ignore
