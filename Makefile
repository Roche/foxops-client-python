.PHONY: clean-test-infrastructure
clean:
	docker ps -aq --filter "label=creator=pytest-docker-tools" | xargs docker rm -f
	docker volume ls --filter "label=creator=pytest-docker-tools" --format '{{ .Name }}' | xargs docker volume rm
	docker network ls --filter "label=creator=pytest-docker-tools" --format '{{ .Name }}' | xargs docker network rm

fmt:
	poetry run black src tests
	poetry run isort src tests

lint:
	poetry run black --check --diff src tests
	poetry run isort --check-only src tests
	poetry run flake8 src tests

typecheck:
	poetry run dmypy run -- src tests

pre-commit: fmt lint typecheck
