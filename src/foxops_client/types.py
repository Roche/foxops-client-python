from enum import Enum
from typing import Any

from pydantic import BaseModel


class MergeRequestStatus(Enum):
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"
    UNKNOWN = "unknown"


class Incarnation(BaseModel):
    id: int
    incarnation_repository: str
    target_directory: str

    commit_sha: str
    commit_url: str

    merge_request_id: str | None
    merge_request_url: str | None


class IncarnationWithDetails(Incarnation):
    # no longer including "status" field as it's deprecated in foxops
    merge_request_status: MergeRequestStatus | None

    template_repository: str | None
    template_repository_version: str | None
    template_repository_version_hash: str | None
    template_data: dict[str, Any] | None
