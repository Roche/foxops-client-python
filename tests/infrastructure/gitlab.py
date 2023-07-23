import uuid
from tempfile import TemporaryDirectory
from time import sleep
from urllib.parse import quote

import httpx
from git import Repo
from infrastructure._common import NAME_PREFIX
from pytest import fixture
from pytest_docker_tools import container, fetch, volume, wrappers

GITLAB_LISTEN_PORT = 12080
GITLAB_ROOT_PASSWORD = "foxops_acceptance_tests"
GITLAB_CONFIG = f"""
external_url 'http://{NAME_PREFIX}_gitlab:{GITLAB_LISTEN_PORT}'
nginx['listen_port'] = {GITLAB_LISTEN_PORT}
"""

# Images
gitlab_image = fetch(repository="gitlab/gitlab-ce:15.6.0-ce.0")

# Volumes
gitlab_config_volume = volume(
    name=f"{NAME_PREFIX}_gitlab_config",
    initial_content={
        "gitlab.rb": GITLAB_CONFIG.encode(),
    },
    scope="session",
)
gitlab_data_volume = volume(
    name=f"{NAME_PREFIX}_gitlab_data",
    scope="session",
)
gitlab_logs_volume = volume(
    name=f"{NAME_PREFIX}_gitlab_logs",
    scope="session",
)


# Container
class GitlabContainer(wrappers.Container):
    def __init__(self, *kargs, **kwargs):
        super().__init__(*kargs, **kwargs)

        self.host_port = None
        self.host_url = None

    def ready(self):
        if not super().ready():
            return False

        self.host_port = self.ports[f"{GITLAB_LISTEN_PORT}/tcp"][0]
        self.host_url = f"http://localhost:{self.host_port}"

        # we want gitlab to return a 200 several times in a row.
        # especially in the github runners it can act flaky otherwise.
        for _ in range(3):
            response = httpx.get(self.host_url, follow_redirects=True)
            if response.status_code != 200:
                return False

            sleep(5)

        return True


gitlab_container = container(
    name=f"{NAME_PREFIX}_gitlab",
    image="{gitlab_image.id}",
    environment={
        "GITLAB_ROOT_PASSWORD": GITLAB_ROOT_PASSWORD,
    },
    network="{network.name}",
    ports={
        f"{GITLAB_LISTEN_PORT}/tcp": None,
    },
    volumes={
        "{gitlab_config_volume.name}": {"bind": "/etc/gitlab", "mode": "rw"},
        "{gitlab_data_volume.name}": {"bind": "/var/opt/gitlab", "mode": "rw"},
        "{gitlab_logs_volume.name}": {"bind": "/var/log/gitlab", "mode": "rw"},
    },
    scope="session",
    timeout=15 * 60,
    wrapper_class=GitlabContainer,
)


@fixture(scope="session")
def gitlab_host_port(gitlab_container):
    return gitlab_container.ports[f"{GITLAB_LISTEN_PORT}/tcp"][0]


@fixture(scope="session")
def gitlab_docker_network_url():
    gitlab_url = f"http://{NAME_PREFIX}_gitlab:{GITLAB_LISTEN_PORT}"
    return gitlab_url


@fixture(scope="session")
def gitlab_host_url(gitlab_host_port):
    gitlab_url = f"http://localhost:{gitlab_host_port}"
    return gitlab_url


@fixture(scope="session")
def gitlab_access_token(gitlab_host_url):
    auth_client = httpx.Client(base_url=gitlab_host_url)
    response = auth_client.post(
        "/oauth/token",
        data={
            "grant_type": "password",
            "username": "root",
            "password": GITLAB_ROOT_PASSWORD,
        },
    )
    response.raise_for_status()

    temp_token = response.json()["access_token"]

    api_client = httpx.Client(
        base_url=gitlab_host_url,
        headers={
            "Authorization": f"Bearer {temp_token}",
        },
    )
    response = api_client.post(
        "/api/v4/users/1/personal_access_tokens",
        json={
            "name": "foxops_acceptance_tests",
            "scopes": ["api"],
        },
    )
    response.raise_for_status()

    access_token = response.json()["token"]
    access_token_id = response.json()["id"]

    yield access_token

    api_client.delete(
        f"/api/v4/personal_access_tokens/{access_token_id}",
    )


@fixture(scope="session")
def gitlab_access_token_binary(gitlab_access_token) -> bytes:
    return gitlab_access_token.encode()


@fixture()
def gitlab_api_client(gitlab_host_url, gitlab_access_token):
    client = httpx.Client(
        base_url=gitlab_host_url + "/api/v4",
        headers={
            "Authorization": f"Bearer {gitlab_access_token}",
        },
    )
    return client


@fixture
def gitlab_project_factory(gitlab_api_client):
    """Returns a factory for new GitLab projects.

    Created projects are recorded and automatically deleted at the end of the test"""

    project_ids = []

    def create_project(return_path: bool = False) -> int | str:
        random_id = uuid.uuid4().hex[:8]
        response = gitlab_api_client.post(
            "/projects",
            json={
                "name": f"foxops_acceptance_tests-{random_id}",
                "visibility": "private",
            },
        )
        response.raise_for_status()

        project_id = int(response.json()["id"])
        project_ids.append(project_id)

        if return_path:
            return response.json()["path_with_namespace"]
        else:
            return project_id

    yield create_project

    for id_to_delete in project_ids:
        gitlab_api_client.delete(f"/projects/{id_to_delete}")


@fixture
def locally_cloned_gitlab_project(
    gitlab_api_client, gitlab_project_factory, gitlab_docker_network_url, gitlab_host_url, gitlab_access_token
):
    """Clone an empty Gitlab project into a temporary directory.

    Yields the project ID and a GitPython Repo object of the local clone."""

    project_id = gitlab_project_factory()
    http_url = gitlab_api_client.get(f"/projects/{project_id}").json()["http_url_to_repo"]

    # transform the URL to one that is accessible from outside the Docker network
    http_url = http_url.replace(gitlab_docker_network_url, gitlab_host_url)

    # inject username and password into the URL
    encoded_username = quote("__token__", safe="")
    encoded_password = quote(gitlab_access_token, safe="")
    http_url = http_url.replace("://", f"://{encoded_username}:{encoded_password}@", 1)

    with TemporaryDirectory() as tempdir:
        repo = Repo.clone_from(http_url, tempdir)
        yield project_id, repo
