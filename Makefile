PROJECT_NAME := $(shell basename $(PWD))
COMPOSE_FILE := compose.yml
COMPOSE_TEMPLATE := compose.template.yml
COMPOSE_PROD_FILE := compose.prod.yml
COMPOSE_PROD_TEMPLATE := compose.prod.template.yml

prepare-compose:
	sed 's/serviceName/$(PROJECT_NAME)/g' $(COMPOSE_TEMPLATE) > $(COMPOSE_FILE)

up: prepare-compose
	docker-compose up -d

down:
	docker-compose down

clean:
	rm -f $(COMPOSE_FILE)
