IMAGE_NAME=prescience-client

DEFAULT_TOKEN=default_token
DEFAULT_PRESCIENCE_API=https://prescience-api.ai.ovh.net
DEFAULT_PRESCIENCE_ADMIN_API=$(DEFAULT_PRESCIENCE_API)
DEFAULT_PRESCIENCE_WEBSOCKET=wss://prescience-websocket.ai.ovh.net
DEFAULT_PRESCIENCE_SERVING_URL=https://prescience-serving.ai.ovh.net

DOCKER_OPT=-it

.DEFAULT_GOAL := all

all: build_docker lint_docker test_docker test_integration_docker

build_docker:
	docker build -t $(IMAGE_NAME) \
	--build-arg DEFAULT_TOKEN=$(DEFAULT_TOKEN) \
	--build-arg DEFAULT_PRESCIENCE_API=$(DEFAULT_PRESCIENCE_API) \
	--build-arg DEFAULT_PRESCIENCE_WEBSOCKET=$(DEFAULT_PRESCIENCE_WEBSOCKET) \
	--build-arg DEFAULT_PRESCIENCE_ADMIN_API_URL=$(DEFAULT_PRESCIENCE_ADMIN_API) \
	--build-arg DEFAULT_PRESCIENCE_SERVING_URL=$(DEFAULT_PRESCIENCE_SERVING_URL) \
	.

test_local:
	cd tests/ && export PYTHONPATH=../ && pytest

test_integration:
	cd tests_integration/ && export PYTHONPATH=../ && pytest -s

test_docker:
	docker run --rm $(DOCKER_OPT) --entrypoint=sh prescience-client -c "make test_local"

test_integration_docker:
	docker run --rm $(DOCKER_OPT) --entrypoint=sh prescience-client -c "make test_integration"

lint_local:
	pylint --rcfile=misc/pylintrc prescience
	pylint --rcfile=misc/pylintrc prescience_client/
	pylint --rcfile=misc/pylintrc tests/
	pylint --rcfile=misc/pylintrc tests_integration/

lint_docker:
	docker run --rm $(DOCKER_OPT) --entrypoint=sh prescience-client -c "make lint_local"

run_local:
	python -i -c "from prescience_client import prescience"

run_docker:
	docker run --rm $(DOCKER_OPT) prescience-client

install_local:
	pip install -e .
