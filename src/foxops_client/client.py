import logging
from typing import Any, Tuple

import httpx
from httpx import Response

from foxops_client.retries import default_retry
from foxops_client.types import Incarnation, IncarnationWithDetails


class AuthenticationError(Exception):
    pass


class FoxOpsApiError(Exception):
    def __init__(self, message: str):
        super().__init__()
        self.message = message


class IncarnationDoesNotExistError(FoxOpsApiError):
    pass


class FoxOpsClient:
    """
    This class can be used to call the FoxOps API.

    It only exposes the API as-is, meaning it only takes care of doing the HTTP requests with retries,
    error handling and type conversions. Methods map to API endpoints 1:1.

    It does not contain any business logic.
    """

    def __init__(self, base_url: str, token: str):
        self.retry_function = default_retry()

        self.log: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {token}"},
            verify=True,
            timeout=httpx.Timeout(120.0, connect=60.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    def _handle_unexpected_response(self, resp: Response):
        if resp.status_code == httpx.codes.UNAUTHORIZED:
            self.log.error(f"Authentication failed with status code 401: {resp.text}")
            raise AuthenticationError()

        self.log.error(f"received unexpected response from FoxOps API: {resp.status_code} {resp.headers} {resp.text}")
        self.log.error(f"request: {resp.request.method} {resp.request.url}")

        resp.raise_for_status()

    def verify_token(self):
        response = self.retry_function(self.client.get)("/auth/test")

        if response.status_code == httpx.codes.OK:
            return

        self._handle_unexpected_response(response)
        raise ValueError("unexpected response")

    def list_incarnations(
        self, incarnation_repository: str | None = None, target_directory: str | None = None
    ) -> list[Incarnation]:
        params = {}
        if incarnation_repository is not None:
            params["incarnation_repository"] = incarnation_repository
        if target_directory is not None:
            params["target_directory"] = target_directory

        resp = self.retry_function(self.client.get)("/api/incarnations", params=params)

        match resp.status_code:
            case httpx.codes.OK:
                return [Incarnation(**x) for x in resp.json()]
            case httpx.codes.NOT_FOUND:
                raise IncarnationDoesNotExistError(resp.json()["message"])

        self._handle_unexpected_response(resp)
        raise ValueError("unexpected response")

    def get_incarnation(self, incarnation_id: int) -> IncarnationWithDetails:
        resp = self.retry_function(self.client.get)(f"/api/incarnations/{incarnation_id}")

        match resp.status_code:
            case httpx.codes.OK:
                return IncarnationWithDetails(**resp.json())
            case httpx.codes.NOT_FOUND:
                raise IncarnationDoesNotExistError(resp.json()["message"])

        self._handle_unexpected_response(resp)
        raise ValueError("unexpected response")

    def delete_incarnation(self, incarnation_id: int):
        resp = self.retry_function(self.client.delete)(f"/api/incarnations/{incarnation_id}")

        match resp.status_code:
            case httpx.codes.NO_CONTENT:
                return
            case httpx.codes.NOT_FOUND:
                raise IncarnationDoesNotExistError(resp.json()["message"])

        self._handle_unexpected_response(resp)
        raise ValueError("unexpected response")

    def update_incarnation(
        self,
        incarnation_id: int,
        automerge: bool,
        template_repository_version: str | None = None,
        template_data: dict[str, str] | None = None,
    ) -> IncarnationWithDetails:
        data: dict[str, Any] = {
            "automerge": automerge,
        }
        if template_repository_version is not None:
            data["template_repository_version"] = template_repository_version
        if template_data is not None:
            data["template_data"] = template_data

        resp = self.retry_function(self.client.put)(f"/api/incarnations/{incarnation_id}", json=data)

        match resp.status_code:
            case httpx.codes.OK:
                return IncarnationWithDetails(**resp.json())
            case httpx.codes.NOT_FOUND:
                raise IncarnationDoesNotExistError(resp.json()["message"])
            case httpx.codes.BAD_REQUEST | httpx.codes.CONFLICT:
                self.log.error(f"received error from FoxOps API: {resp.status_code} {resp.headers} {resp.text}")
                raise FoxOpsApiError(resp.json()["message"])

        self._handle_unexpected_response(resp)
        raise ValueError("unexpected response")

    def create_incarnation(
        self,
        incarnation_repository: str,
        template_repository: str,
        template_repository_version: str,
        template_data: dict[str, str],
        target_directory: str | None = None,
        automerge: bool | None = None,
        allow_import: bool | None = None,
    ) -> Tuple[bool, IncarnationWithDetails]:
        """
        Call the FoxOps API to create a new incarnation.

        Returns a tuple of (imported, incarnation), where imported is a boolean that is True if the incarnation
        already existed and was added to the foxops inventory. This can only be True if the allow_import parameter
        is set to True.
        """
        data: dict[str, Any] = {
            "incarnation_repository": incarnation_repository,
            "template_repository": template_repository,
            "template_repository_version": template_repository_version,
            "template_data": template_data,
        }
        if target_directory is not None:
            data["target_directory"] = target_directory
        if automerge is not None:
            data["automerge"] = automerge

        params = {}
        if allow_import is not None:
            params["allow_import"] = allow_import

        resp = self.retry_function(self.client.post)("/api/incarnations", params=params, json=data)

        match resp.status_code:
            case httpx.codes.OK:
                return True, IncarnationWithDetails(**resp.json())
            case httpx.codes.CREATED:
                return False, IncarnationWithDetails(**resp.json())
            case httpx.codes.BAD_REQUEST:
                self.log.error(f"received error from FoxOps API: {resp.status_code} {resp.headers} {resp.text}")
                raise FoxOpsApiError(resp.json()["message"])

        self._handle_unexpected_response(resp)
        raise ValueError("unexpected response")
