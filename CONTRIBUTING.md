# Contributing

## Tests

The foxops API client relies mostly on e2e tests that execute calls against a running foxops (and Gitlab) server. The tests are located in the `tests` directory and are executed using `pytest`.

All the necessary test environment is spun up locally using docker images and the `pytest-docker-tools` plugin. You can find the relevant fixtures in the `tests/infrastucture` directory.

No additional configuration is needed to run the tests. The only requirement is that you have a running docker daemon.

```shell
# Executing all tests from a "cold start" could take a while as the Gitlab docker image takes 2-3 minutes to start
poetry run pytest

# instead, especially during development, it's recommended to keep the Gitlab container running and not terminate it at the end.
poetry run pytest --reuse-containers
```
