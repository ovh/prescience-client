IMAGE_NAME=prescience-client
DEFAULT_TOKEN=default_token

.DEFAULT_GOAL := all

all: build_docker lint_docker test_docker test_integration_docker

build_docker:
	docker build -t $(IMAGE_NAME) --build-arg DEFAULT_TOKEN=$(DEFAULT_TOKEN) .

test_local:
	cd tests/ && export PYTHONPATH=../ && pytest

test_integration:
	cd tests_integration/ && export PYTHONPATH=../ && pytest -s

test_docker:
	docker run --rm -it --entrypoint=sh prescience-client -c "make test_local"

test_integration_docker:
	docker run --rm -it --entrypoint=sh prescience-client -c "make test_integration"

lint_local:
	pylint --rcfile=misc/pylintrc prescience_client.py
	pylint --rcfile=misc/pylintrc com/
	pylint --rcfile=misc/pylintrc tests/
	pylint --rcfile=misc/pylintrc tests_integration/

lint_docker:
	docker run --rm -it --entrypoint=sh prescience-client -c "make lint_local"
