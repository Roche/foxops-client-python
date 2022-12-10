.PHONY: clean-test-infrastructure
clean-test-infrastructure:
	docker ps -aq --filter "label=creator=pytest-docker-tools" | xargs docker rm -f
