from infrastructure._common import NAME_PREFIX
from pytest_docker_tools import network

network = network(
    name=f"{NAME_PREFIX}_network",
    driver="bridge",
    scope="session",
)
