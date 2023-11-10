from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Self


TemplateData = dict[str, Any]


class MergeRequestStatus(Enum):
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Incarnation:
    id: int
    incarnation_repository: str
    target_directory: str

    commit_sha: str
    commit_url: str

    merge_request_id: str | None
    merge_request_url: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data["id"],
            incarnation_repository=data["incarnation_repository"],
            target_directory=data["target_directory"],
            commit_sha=data["commit_sha"],
            commit_url=data["commit_url"],
            merge_request_id=data["merge_request_id"],
            merge_request_url=data["merge_request_url"],
        )


@dataclass(frozen=True)
class IncarnationWithDetails(Incarnation):
    merge_request_status: MergeRequestStatus | None

    template_repository: str | None
    template_repository_version: str | None
    template_repository_version_hash: str | None
    template_data: TemplateData | None
    template_data_full: TemplateData | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        merge_request_status = None
        if data["merge_request_status"] is not None:
            merge_request_status = MergeRequestStatus(data["merge_request_status"])

        return cls(
            merge_request_status=merge_request_status,
            template_repository=data["template_repository"],
            template_repository_version=data["template_repository_version"],
            template_repository_version_hash=data["template_repository_version_hash"],
            template_data=data["template_data"],
            template_data_full=data["template_data_full"],
            **asdict(Incarnation.from_dict(data)),
        )
