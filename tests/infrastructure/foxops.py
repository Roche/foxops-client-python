from infrastructure._common import NAME_PREFIX
from infrastructure.gitlab import gitlab_access_token_binary, gitlab_docker_network_url
from pytest import fixture
from pytest_docker_tools import container, fetch, volume, wrappers

FOXOPS_LISTEN_PORT = "8000/tcp"
FOXOPS_STATIC_TOKEN = "dummy"

# Images
foxops_image = fetch(repository="ghcr.io/roche/foxops:db2d36a4fae02df57a9559c35ad1256bffae3b4c")

# Volumes
foxops_secrets_volume = volume(
    name=f"{NAME_PREFIX}_foxops_secrets",
    initial_content={
        "foxops_gitlab_token": gitlab_access_token_binary,
    },
    scope="session",
)


# Containers
class FoxOpsContainer(wrappers.Container):
    def ready(self):
        if not super().ready():
            return False

        # mark as ready if an error or warning was logged
        if "error" in self.logs().lower() or "warn" in self.logs().lower():
            return True

        return self.logs().find("Uvicorn running on") != -1


foxops_container = container(
    image="{foxops_image.id}",
    name=NAME_PREFIX + "_foxops",
    environment={
        "FOXOPS_GITLAB_ADDRESS": gitlab_docker_network_url,
        "FOXOPS_STATIC_TOKEN": FOXOPS_STATIC_TOKEN,
    },
    command=[
        "/bin/bash", "-c",
        "alembic upgrade head && uvicorn foxops.__main__:create_app --factory --host 0.0.0.0 --port 8000"
    ],
    volumes={
        "{foxops_secrets_volume.name}": {"bind": "/var/run/secrets/foxops", "mode": "ro"},
    },
    ports={
        FOXOPS_LISTEN_PORT: None,
    },
    network="{network.name}",
    scope="session",
    wrapper_class=FoxOpsContainer,
)


@fixture(scope="session")
def foxops_host_port(foxops_container: FoxOpsContainer):
    return foxops_container.ports[FOXOPS_LISTEN_PORT][0]


@fixture(scope="session")
def foxops_host_url(foxops_host_port):
    return f"http://localhost:{foxops_host_port}"
