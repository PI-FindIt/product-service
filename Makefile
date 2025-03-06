OS := $(shell uname)
ifeq ($(OS),Darwin)
	EXECUTABLES = gsed gtr
	K := $(foreach exec,$(EXECUTABLES),\
			$(if $(shell which $(exec)),some string,$(error "No GNU tools installed on macOS, consider installing using brew")))
	SED := gsed
	TR := gtr
else
	SED := sed
	TR := tr
endif

PROJECT_NAME := $(shell basename $(PWD))
PROJECT_NAME_SNAKE_CASE := $(shell echo $(PROJECT_NAME) | $(TR) '-' '_')

TEMPLATE_FOLDER := ./templates
COMPOSE_FILE := compose.yaml
COMPOSE_TEMPLATE := $(TEMPLATE_FOLDER)/compose.template.yaml
COMPOSE_PROD_FILE := compose.prod.yaml
COMPOSE_PROD_TEMPLATE := $(TEMPLATE_FOLDER)/compose.prod.template.yaml

DOCKERFILE := Dockerfile
DOCKERFILE_TEMPLATE := $(TEMPLATE_FOLDER)/Dockerfile.template

DOCKERFILE_PROD := Dockerfile.prod
DOCKERFILE_PROD_TEMPLATE := $(TEMPLATE_FOLDER)/Dockerfile.template.prod

WORKFLOW_TEMPLATE := $(TEMPLATE_FOLDER)/submodule.template.yaml
WORKFLOW_FILE := .github/workflows/submodule.yaml

PROTOBUF_FOLDER := protobuf/$(PROJECT_NAME_SNAKE_CASE)
PROTOBUF_SERVICE_FILE := $(PROTOBUF_FOLDER)/service.proto
PROTOBUF_SERVICE_FILE_TEMPLATE := $(TEMPLATE_FOLDER)/service.template.proto
PROTOBUF_SERVICE_SERVER := src/api/service.py
PROTOBUF_SERVICE_SERVER_TEMPLATE := $(TEMPLATE_FOLDER)/service.template.py

all: dev prod protobuf-create protobuf-gen

prepare-compose:
	$(SED) 's/serviceName/$(PROJECT_NAME)/g' $(COMPOSE_TEMPLATE) > $(COMPOSE_FILE)

prepare-compose-prod:
	$(SED) 's/serviceName/$(PROJECT_NAME)/g' $(COMPOSE_PROD_TEMPLATE) > $(COMPOSE_PROD_FILE)

prepare-dockerfile:
	$(SED) 's/serviceName/$(PROJECT_NAME)/g' $(DOCKERFILE_TEMPLATE) > $(DOCKERFILE)

prepare-dockerfile-prod:
	$(SED) 's/serviceName/$(PROJECT_NAME)/g' $(DOCKERFILE_PROD_TEMPLATE) > $(DOCKERFILE_PROD)

prepare-workflow:
	mkdir -p .github/workflows
	$(SED) 's/serviceName/$(PROJECT_NAME)/g' $(WORKFLOW_TEMPLATE) > $(WORKFLOW_FILE)

protobuf-gen:
	python -m grpc_tools.protoc -I=$(PROTOBUF_FOLDER) --python_out=$(PROTOBUF_FOLDER) --grpc_python_out=$(PROTOBUF_FOLDER) $(PROTOBUF_SERVICE_FILE)

protobuf-create:
	git submodule update --init --recursive
	mkdir -p $(PROTOBUF_FOLDER)
	touch $(PROTOBUF_FOLDER)/__init__.py
	cp $(PROTOBUF_SERVICE_FILE_TEMPLATE) $(PROTOBUF_SERVICE_FILE)
	$(SED) 's/service_name/$(PROJECT_NAME_SNAKE_CASE)/g' $(PROTOBUF_SERVICE_SERVER_TEMPLATE) > $(PROTOBUF_SERVICE_SERVER)

dev: prepare-dockerfile prepare-compose prepare-workflow

prod: prepare-dockerfile-prod prepare-compose-prod prepare-workflow

up:
	@if [ ! -f compose.yaml ]; then \
		$(MAKE) prepare-dockerfile; \
		$(MAKE) prepare-compose; \
	fi
	docker compose up -d

up-prod:
	@if [ ! -f compose.prod.yaml ]; then \
		$(MAKE) prepare-dockerfile-prod; \
		$(MAKE) prepare-compose-prod; \
	fi
	docker compose -f $(COMPOSE_PROD_FILE) up -d

down:
	docker compose down

clean:
	rm -f $(COMPOSE_FILE) $(COMPOSE_PROD_FILE) $(DOCKERFILE) $(DOCKERFILE_PROD) $(WORKFLOW_FILE) $(PROTOBUF_SERVICE_SERVER)
	rm -rf $(PROTOBUF_FOLDER)

help:
	@echo "Targets:"
	@echo "  prepare-compose  Prepare the compose file"
	@echo "  up               Start the project"
	@echo "  down             Stop the project"
	@echo "  clean            Clean up the project"
	@echo "  help             Show this help message"
