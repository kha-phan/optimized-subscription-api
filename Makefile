COMPOSE_COMMAND := docker compose -f docker-compose.yml

COMPOSE_RUN_APP = $(COMPOSE_COMMAND) run --rm --entrypoint bash app
COMPOSE_RUN_DB = $(COMPOSE_COMMAND) run --rm --entrypoint bash db
COMPOSE_RUN_PYTHON = $(COMPOSE_COMMAND) run --rm --entrypoint bash python

shellPython: .env
    $(COMPOSE_RUN_PYTHON)
.PHONY: shellPython
