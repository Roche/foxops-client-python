.PHONY: clean-test-infrastructure
clean:
	docker ps -aq --filter "label=creator=pytest-docker-tools" | xargs docker rm -f
	docker volume ls --filter "label=creator=pytest-docker-tools" --format '{{ .Name }}' | xargs docker volume rm
	docker network ls --filter "label=creator=pytest-docker-tools" --format '{{ .Name }}' | xargs docker network rm
