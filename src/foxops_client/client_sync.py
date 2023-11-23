import asyncio
from typing import Any

from foxops_client.client_async import AsyncFoxopsClient
from foxops_client.types import Incarnation, IncarnationWithDetails


class FoxopsClient:
    """
    This class can be used to call the FoxOps API.

    It only exposes the API as-is, meaning it only takes care of doing the HTTP requests with retries,
    error handling and type conversions. Methods map to API endpoints 1:1.

    It does not contain any business logic.

    This synchronous version of the foxops client is merely a thin wrapper around the async version.
    """

    def __init__(self, base_url: str, token: str):
        self.client = AsyncFoxopsClient(base_url, token)

        self.loop = asyncio.new_event_loop()

    def verify_token(self):
        return self.loop.run_until_complete(self.client.verify_token())

    def list_incarnations(
        self, incarnation_repository: str | None = None, target_directory: str | None = None
    ) -> list[Incarnation]:
        return self.loop.run_until_complete(self.client.list_incarnations(incarnation_repository, target_directory))

    def get_incarnation(self, incarnation_id: int) -> IncarnationWithDetails:
        return self.loop.run_until_complete(self.client.get_incarnation(incarnation_id))

    def delete_incarnation(self, incarnation_id: int):
        return self.loop.run_until_complete(self.client.delete_incarnation(incarnation_id))

    def patch_incarnation(
        self,
        incarnation_id: int,
        automerge: bool,
        requested_version: str | None = None,
        requested_data: dict[str, Any] | None = None,
    ):
        return self.loop.run_until_complete(
            self.client.patch_incarnation(
                incarnation_id,
                automerge,
                requested_version=requested_version,
                requested_data=requested_data,
            )
        )

    def put_incarnation(
        self,
        incarnation_id: int,
        automerge: bool,
        template_repository_version: str,
        template_data: dict[str, Any],
    ) -> IncarnationWithDetails:
        return self.loop.run_until_complete(
            self.client.put_incarnation(
                incarnation_id,
                automerge,
                template_repository_version=template_repository_version,
                template_data=template_data,
            )
        )

    def create_incarnation(
        self,
        incarnation_repository: str,
        template_repository: str,
        template_repository_version: str,
        template_data: dict[str, Any],
        target_directory: str | None = None,
        automerge: bool | None = None,
    ) -> IncarnationWithDetails:
        return self.loop.run_until_complete(
            self.client.create_incarnation(
                incarnation_repository,
                template_repository,
                template_repository_version,
                template_data,
                target_directory=target_directory,
                automerge=automerge,
            )
        )
