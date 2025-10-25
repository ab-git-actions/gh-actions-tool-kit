# gh-actions-tool-kit

A lightweight, typed Python-based toolkit inspired by [`@actions/core`](https://github.com/actions/toolkit/tree/main/packages/core) and [`actions/github`](https://github.com/actions/toolkit/tree/main/packages/github), this library provides:

- 🔍 A `Context` class to access GitHub Action runtime metadata
- 📦 A `WebhookPayload` parser to load and normalize GitHub webhook events
- 🧠 Models for structured data access (`RepoIdentifier`, `IssueIdentifier`, etc.)
- 🐙 A helper for creating authenticated PyGitHub clients


---

## 🚀 Quick Start

### Installation
```bash
pip install gh-actions-tool-kit
```

## Usage

### Actions Core Example


```python
# ================================
# greeting.py
# ================================

from actions_tool_kit import get_input, set_output, notice, group

def main() -> None:
    name = get_input("name", required=True)
    with group("Greeting"):
        message = f"Hello, {name}!"
        notice(message, title="Python Action")
        set_output("greeting", message)

if __name__ == "__main__":
    main()
```

#### 🧩 Features

| **Feature**                           | **Description**                                                                                                      |
|---------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `get_input(name)`                     | Retrieves the value of an input defined in the GitHub Action `with:` section.                                        |
| `get_boolean_input(name)`             | Retrieves a boolean input value (`true` or `false`) from the `with:` section, automatically parsing it.              |
| `set_output(name, value)`             | Sets an output parameter for the step, which can be used by subsequent steps.                                        |
| `export_variable(name, value)`        | Sets an environment variable that will be available to all subsequent steps in the job.                              |
| `add_path(path)`                      | Prepends a directory to the system `PATH` variable for all subsequent steps in the job.                              |
| `save_state(name, value)`             | Saves state data that can be retrieved later using `get_state()` in a post-run step. Useful for cleanup or teardown. |
| `get_state(name)`                     | Retrieves state saved by `save_state()` earlier in the job. Commonly used in `post:` scripts.                        |
| `set_secret(secret)`                  | Masks a string from logs to prevent it from being exposed in the GitHub Actions output.                              |
| `append_summary(markdown)`            | Appends markdown content to the GitHub Actions job summary (visible in the UI under the job).                        |
| `notice(message)`                     | Displays a **notice** message in the Actions logs.                                                                   |
| `warning(message)`                    | Displays a **warning** message in the Actions logs, usually in yellow.                                               |
| `error(message)`                      | Displays an **error** message in the Actions logs, usually in red.                                                   |
| `debug(message)`                      | Sends a debug log message, visible only if step debugging is enabled.                                                |
| `group(title)` / `start_group(title)` | Starts a collapsible log group with a given title.                                                                   |
| `end_group()`                         | Ends the most recent collapsible log group.                                                                          |


### Action Context Example

```python
from actions_tool_kit import context

# Basic metadata
print(context.event_name)  # "pull_request"
print(context.sha)         # commit SHA
print(context.ref)         # branch ref
print(context.actor)       # user who triggered

# Repo info
print(context.repo.owner)  # "your-org"
print(context.repo.repo)   # "your-repo"

# Issue or PR
print(context.issue.number)  # 42

# Access webhook payload
print(context.payload.pull_request.get("title"))
```

#### 🧩 Context Properties Features

| Property    | Type                  | Description                           |
|-------------|-----------------------|---------------------------------------|
| event_name  | str                   | Event type (e.g., push, pull_request) |
| ref         | str                   | Git ref that triggered the workflow   |
| sha         | str                   | Commit SHA                            |
| workflow    | str                   | Workflow name                         |
| actor       | str                   | Actor triggering the event            |
| job         | str                   | Job name                              |
| run_id      | int                   | Unique run ID                         |
| run_number  | int                   | Run number                            |
| run_attempt | int                   | Retry number for the run              |
| api_url     | str                   | GitHub API URL                        |
| server_url  | str                   | GitHub server URL                     |
| graphql_url | str                   | GraphQL endpoint                      |
| repo        | RepoIdentifier        | owner and repo parsed                 |
| issue       | IssueIdentifier       | repo + issue/pull number              |
| pr          | PullRequestIdentifier | repo + PR number                      |
| head_branch | str                   | For PR events: source branch          |
| base_branch | str                   | For PR events: target branch          |
| sender      | Sender                | Structured sender info                |

### 📄 Webhook Payload Parser

* The parse_payload() function:
  * Parses the JSON in $GITHUB_EVENT_PATH
  * Normalizes fields like repository, sender, issue, pull_request
  * Loads it into a structured WebhookPayload dataclass

> [!NOTE]
> You don’t need to call this manually — Context does it for you.

### 🧱 Models

| Class                   | Description                       |
|-------------------------|-----------------------------------|
| `RepoOwner`             | `login`, `name`, `extra`          |
| `PayloadRepository`     | `name`, `owner`, `html_url`, etc. |
| `WebhookPayload`        | Top-level GitHub event structure  |
| `RepoIdentifier`        | `{owner, repo}`                   |
| `IssueIdentifier`       | `{owner, repo, number}`           |
| `PullRequestIdentifier` | `{owner, repo, number}`           |
| `Sender`                | `{type, login, extra}`            |

### Example Workflow

```yaml
name: demo
on: [push]
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Run Python Action
        env:
          name: <your name>
        run: python greeting.py
```

## 🙌 Credits

Inspired by [`@actions/core`](https://github.com/actions/toolkit/tree/main/packages/core) and [`actions/github`](https://github.com/actions/toolkit/tree/main/packages/github)

## 📄 License

MIT License © 2024 AB
