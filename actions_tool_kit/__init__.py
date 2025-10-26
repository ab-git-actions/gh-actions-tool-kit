__all__ = []

from .actions_core import *

try:
    __all__ += actions_core.__all__
except Exception:
    pass

# Safe import of context and client factory
try:
    from .context import context
    from .github_client import get_github_client

    __all__ += ["context", "get_github_client"]
except ImportError:
    # Allow unit tests to run even if GitHub context/client aren't needed
    pass
