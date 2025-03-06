PROJECT_NAME := $(shell basename $(PWD))
COMPOSE_FILE := compose.yaml
COMPOSE_TEMPLATE := compose.template.yaml
COMPOSE_PROD_FILE := compose.prod.yaml
COMPOSE_PROD_TEMPLATE := compose.prod.template.yaml

prepare-compose:
	sed 's/serviceName/$(PROJECT_NAME)/g' $(COMPOSE_TEMPLATE) > $(COMPOSE_FILE)

up: prepare-compose
	docker compose up -d

down:
	docker compose down

clean:
	rm -f $(COMPOSE_FILE)
