# actions_core.py
# Minimal Python equivalent of @actions/core for GitHub Actions
# Usage: from actions_core import *
from __future__ import annotations
import os
import sys
from contextlib import contextmanager
from typing import Optional, Iterable

# ---------- internals ----------
def _file_from_env(var: str) -> Optional[str]:
    p = os.getenv(var)
    return p if p and p.strip() else None

def _append_line(filepath: str, line: str) -> None:
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")

def _serialize_props(**props) -> str:
    # Convert None/empty to omitted; escape chars per runner rules
    # https://docs.github.com/actions/using-workflows/workflow-commands-for-github-actions
    def esc(val: str) -> str:
        return (
            str(val)
            .replace("%", "%25")
            .replace("\r", "%0D")
            .replace("\n", "%0A")
            .replace(":", "%3A")
            .replace(",", "%2C")
        )
    items = [f"{k}={esc(v)}" for k, v in props.items() if v not in (None, "", False)]
    return " " + ",".join(items) if items else ""

def _cmd(command: str, message: str = "", **props) -> None:
    sys.stdout.write(f"::{command}{_serialize_props(**props)}::{_escape_msg(message)}\n")
    sys.stdout.flush()

def _escape_msg(msg: str) -> str:
    return (
        str(msg)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )

# ---------- inputs ----------
def get_input(name: str, *, required: bool = False, trim: bool = True, default: Optional[str] = None) -> str:
    key = f"INPUT_{name.replace(' ', '_').upper()}"
    val = os.getenv(key)
    if val is None or val == "":
        if default is not None:
            return default
        if required:
            set_failed(f"Input required and not supplied: {name}")
            raise RuntimeError(f"Missing required input: {name}")
        return ""
    return val.strip() if trim else val

def get_boolean_input(name: str, **kwargs) -> bool:
    val = get_input(name, **kwargs)
    return val.strip().lower() in {"1", "true", "t", "yes", "y", "on"}

# ---------- outputs / env / path / state / summary ----------
def set_output(name: str, value: str) -> None:
    path = _file_from_env("GITHUB_OUTPUT")
    if not path:
        # Fallback to legacy command (still useful when testing locally)
        _cmd("set-output", f"{name}={value}")
        return
    _append_line(path, f"{name}={value}")

def export_variable(name: str, value: str) -> None:
    path = _file_from_env("GITHUB_ENV")
    if not path:
        os.environ[name] = value  # local fallback
        return
    _append_line(path, f"{name}={value}")

def add_path(input_path: str) -> None:
    path = _file_from_env("GITHUB_PATH")
    if not path:
        os.environ["PATH"] = f"{input_path}{os.pathsep}{os.environ.get('PATH','')}"
        return
    _append_line(path, input_path)

def save_state(name: str, value: str) -> None:
    path = _file_from_env("GITHUB_STATE")
    if not path:
        # Local fallback: export as env so a later step can read it
        os.environ[f"STATE_{name}"] = value
        return
    _append_line(path, f"{name}={value}")

def get_state(name: str) -> str:
    # Works for local fallback only; in real runner, post-step will read GITHUB_STATE file.
    return os.getenv(f"STATE_{name}", "")

def set_secret(secret: str) -> None:
    _cmd("add-mask", secret)

def append_summary(markdown: str | Iterable[str]) -> None:
    body = "".join(markdown) if not isinstance(markdown, str) else markdown
    path = _file_from_env("GITHUB_STEP_SUMMARY")
    if not path:
        # local preview
        sys.stdout.write("\n--- STEP SUMMARY (local) ---\n" + body + "\n----------------------------\n")
        sys.stdout.flush()
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(body)

# ---------- logging / annotations ----------
def debug(message: str) -> None:
    _cmd("debug", message)

def notice(message: str, *, title: str = None, file: str = None, line: int = None, col: int = None) -> None:
    _cmd("notice", message, title=title, file=file, line=line, col=col)

def warning(message: str, *, title: str = None, file: str = None, line: int = None, col: int = None) -> None:
    _cmd("warning", message, title=title, file=file, line=line, col=col)

def error(message: str, *, title: str = None, file: str = None, line: int = None, col: int = None) -> None:
    _cmd("error", message, title=title, file=file, line=line, col=col)

def set_failed(message: str) -> None:
    error(message)
    # Ensure non-zero exit when used in a script’s main()
    # (If you prefer, raise instead.)
    # Do NOT exit here automatically—let the caller decide.
    # sys.exit(1)

# ---------- groups ----------
def start_group(name: str) -> None:
    _cmd("group", name)

def end_group() -> None:
    _cmd("endgroup")

@contextmanager
def group(name: str):
    start_group(name)
    try:
        yield
    finally:
        end_group()
