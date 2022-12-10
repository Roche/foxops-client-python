from importlib.metadata import version

from foxops_client.client_async import AsyncFoxopsClient
from foxops_client.client_sync import FoxopsClient
from foxops_client.exceptions import (
    AuthenticationError,
    FoxopsApiError,
    IncarnationDoesNotExistError,
)
from foxops_client.types import Incarnation, IncarnationWithDetails, MergeRequestStatus

__version__ = version("foxops_client")

__all__ = [
    "FoxopsClient",
    "AsyncFoxopsClient",
    # Types
    "Incarnation",
    "IncarnationWithDetails",
    "MergeRequestStatus",
    # Exceptions
    "FoxopsApiError",
    "AuthenticationError",
    "IncarnationDoesNotExistError",
]
