SRCDIR = $(shell pwd)
DCF = $(SRCDIR)/docker-compose.yml
EXEC = docker exec
ENV_FILE = --env-file ./.env
REQUIREMENTS_FILE = ./requirements.txt

ENV := $(SRCDIR)/.env

# Environment variables for project
include $(ENV)

# Export all variable to sub-make
export

DC = docker-compose -p $(PROJECT_PREFIX) -f $(DCF)

freeze:
	pip freeze -> $(REQUIREMENTS_FILE)

build:
	$(DC) build

up:
	$(DC) up -d

down:
	$(DC) down

fulldown:
	$(DC) down --rmi local

makemigrations:
	$(EXEC) -it $(PROJECT_PREFIX)_web ./manage.py makemigrations

migrate:
	$(EXEC) -it $(PROJECT_PREFIX)_web ./manage.py migrate

createsuperuser:
	$(EXEC) -it $(PROJECT_PREFIX)_web ./manage.py createsuperuser

collectstatic:
	$(EXEC) -it $(PROJECT_PREFIX)_web ./manage.py collectstatic

