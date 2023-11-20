from pathlib import Path

from infrastructure.foxops import (
    FOXOPS_STATIC_TOKEN,
    foxops_container,
    foxops_database_initialization,
    foxops_host_port,
    foxops_host_url,
    foxops_image,
    foxops_secrets_volume,
)
from infrastructure.gitlab import (
    gitlab_access_token,
    gitlab_access_token_binary,
    gitlab_api_client,
    gitlab_config_volume,
    gitlab_container,
    gitlab_data_volume,
    gitlab_docker_network_url,
    gitlab_host_port,
    gitlab_host_url,
    gitlab_image,
    gitlab_logs_volume,
    gitlab_project_factory,
    locally_cloned_gitlab_project,
)
from infrastructure.network import network
from pytest import fixture

from foxops_client import FoxopsClient

# This variable is never used. We just declare it to mark the imported fixtures as used for linting.
IMPORTED_FIXTURES = [
    foxops_container,
    foxops_host_port,
    foxops_host_url,
    foxops_image,
    foxops_secrets_volume,
    foxops_database_initialization,
    gitlab_access_token,
    gitlab_access_token_binary,
    gitlab_api_client,
    gitlab_config_volume,
    gitlab_container,
    gitlab_data_volume,
    gitlab_docker_network_url,
    gitlab_host_port,
    gitlab_host_url,
    gitlab_image,
    gitlab_logs_volume,
    gitlab_project_factory,
    locally_cloned_gitlab_project,
    network,
]


@fixture
def foxops_client(foxops_host_url):
    return FoxopsClient(foxops_host_url, FOXOPS_STATIC_TOKEN)


@fixture
def foxops_client_invalid_token(foxops_host_url):
    return FoxopsClient(foxops_host_url, FOXOPS_STATIC_TOKEN + "invalid")


@fixture
def template(gitlab_api_client, locally_cloned_gitlab_project):
    """Creates a new foxops template in Gitlab and returns its Path with namespace. Delete it after the test."""

    project_id, repo = locally_cloned_gitlab_project
    root_dir = repo.working_dir

    (Path(root_dir) / "template").mkdir()

    (Path(root_dir) / "template" / "README.md").write_text("{{ input_variable }}")
    (Path(root_dir) / "fengine.yaml").write_text(
        """
variables:
  input_variable:
    type: string
    description: dummy input variable
"""
    )

    repo.git.add(".")
    repo.git.commit("-m", "Initial commit")
    repo.git.push()

    project = gitlab_api_client.get(f"/projects/{project_id}").json()
    path_with_namespace = project["path_with_namespace"]

    yield path_with_namespace
