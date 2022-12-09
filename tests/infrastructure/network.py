from infrastructure._common import NAME_PREFIX
from pytest_docker_tools import network

network = network(
    name=f"{NAME_PREFIX}network",
    driver="bridge",
    scope="session",
)
