SHELL := /bin/sh
APPLICATION_NAME="Find business regulations"

# Colour coding for output
COLOUR_NONE=\033[0m
COLOUR_GREEN=\033[32;01m
COLOUR_YELLOW=\033[33;01m
COLOUR_RED=\033[31;01m

.PHONY: help database drop-database build collectstatic admin first-use up down start stop clean logs test bdd shell shell-local lint black isort
help: # List commands and their descriptions
	@grep -E '^[a-zA-Z0-9_-]+: # .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ": # "; printf "\n\033[93;01m%-30s %-30s\033[0m\n\n", "Command", "Description"}; {split($$1,a,":"); printf "\033[96m%-30s\033[0m \033[92m%s\033[0m\n", a[1], $$2}'

database: # Create a postgres database for the project
	@echo "$(COLOUR_GREEN)Initialising database...$(COLOUR_NONE)"
	docker compose up --force-recreate --remove-orphans -d db
	docker compose exec db createdb -h localhost -U postgres -T template0 fbr
	docker compose stop db
	@echo "$(COLOUR_GREEN)Done$(COLOUR_NONE)"

drop-database: # Delete project's postgres database
	@echo "$(COLOUR_RED)Drop database fbr$(COLOUR_NONE)"
	@read -p "Are you sure? " -n 1 -r; \
		if [[ $$REPLY =~ ^[Yy] ]]; \
		then \
		  	echo ""; \
			echo "$(COLOUR_RED)Dropping database fbr$(COLOUR_NONE)"; \
			docker compose up --force-recreate --remove-orphans -d db; \
			docker compose exec db dropdb -h localhost -U postgres fbr; \
			docker compose stop db; \
			echo "$(COLOUR_GREEN)Done$(COLOUR_NONE)"; \
		else \
			echo "\n$(COLOUR_GREEN)Cancelled$(COLOUR_NONE)"; \
		fi

build: # Build docker containers for local execution
	docker build --no-cache -f Dockerfile -t local_deployment .
	docker compose build

collectstatic: # Run Django collectstatic
	docker compose run --rm web poetry run python manage.py collectstatic --noinput

admin: # Create a superuser
	docker compose exec web poetry run python manage.py createsuperuser --username admin --email admin@localhost

first-use: # Initialise for local execution
	@echo "$(COLOUR_GREEN)Preparing for first use$(COLOUR_NONE)"
	@echo "$(COLOUR_GREEN)Ensuring all containers are stopped...$(COLOUR_NONE)"
	$(MAKE) down
	@echo "$(COLOUR_GREEN)Building...$(COLOUR_NONE)"
	$(MAKE) build
	@echo "$(COLOUR_GREEN)Starting...$(COLOUR_NONE)"
	$(MAKE) up
	@echo "$(COLOUR_GREEN)Initialising web service...$(COLOUR_NONE)"
# $(MAKE) admin
	$(MAKE) stop
	@echo "$(COLOUR_GREEN)$(APPLICATION_NAME) is ready for use$(COLOUR_NONE)";
	@echo "$(COLOUR_GREEN)Start services with 'make start'$(COLOUR_NONE)"
	@echo "$(COLOUR_GREEN)Service is listening on https://localhost:8081$(COLOUR_NONE)"
	@echo "$(COLOUR_GREEN)View logs with 'make logs'$(COLOUR_NONE)"
	@echo "$(COLOUR_GREEN)Shutdown with 'make stop'$(COLOUR_NONE)"
	@echo "$(COLOUR_GREEN)Destroy containers with 'make down'$(COLOUR_NONE)"

up: # Build, (re)create and start containers
	export DATABASE_URL=postgres://postgres:postgres@localhost:5432/fbr
	docker compose up -d
	@echo "$(COLOUR_GREEN)Services are up - use 'make logs' to view service logs$(COLOUR_NONE)"

down: # Stop and remove containers
	docker compose down

start: # Start existing containers
	docker compose start

stop: # Stop running containers without removing them
	docker compose stop

.SILENT: clean
clean: # Remove all fbr containers and images
	docker compose stop
	for i in $$(docker ps -a | awk '$$0!~/IMAGE/ { print $$1 }') ; do \
		echo "Removing container $$i" ; \
		docker rm $$i ; \
	done
	for j in $$(docker images | grep 'none\|local_deployment\|fbr-web' | awk '{ print $$3; }') ; do \
		echo "Removing image $$j" ; \
		docker image rm -f $$j ; \
	done

logs: # View container logs
	docker compose logs -f -t

test: # Run tests
	pytest app/tests --cov-report term

bdd: # Run BDD tests
	HEADLESS_MODE=false SLOW_MO_MS=500 behave ./app/tests/bdd/features/ --tags=LOCAL

django-shell: # Run a Django shell (on  container)
	docker compose run web poetry run python manage.py shell

django-shell-local: # Run a Django shell (local django instance)
	DATABASE_URL=postgres://postgres:postgres@localhost:5432/fbr \
		DEBUG=True \
		DJANGO_ADMIN=False \
		DJANGO_SECRET_KEY=walls-have-ears \
		DJANGO_SETTINGS_MODULE=fbr.settings \
		poetry run python manage.py shell

migrate: # Run Django migrate
	export DATABASE_URL=postgres://postgres:postgres@localhost:5432/fbr && \
	poetry run python manage.py migrate

migrations: # Run Django makemigrations
	export DATABASE_URL=postgres://postgres:postgres@localhost:5432/fbr && \
	python manage.py makemigrations

lint: # Run all linting
	make black
	make isort

black: # Run black
	poetry run black .

isort: # Run isort
	poetry run isort .

secrets-baseline: # Generate a new secrets baseline file
	poetry run detect-secrets scan > .secrets.baseline

# Target to create SSL certificate and key
create-ssl:
	mkdir -p ssl
	openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
	    -keyout $(KEY_FILE) -out $(CERT_FILE) \
	    -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"

rebuild_cache:
	export PYTHONPATH=. && \
	export DJANGO_SETTINGS_MODULE='fbr.settings' && \
	export DATABASE_URL=postgres://postgres:postgres@localhost:5432/fbr && \
	export DEBUG=True && \
	poetry install && \
	poetry run rebuild-cache

setup_local: # Set up the local environment
	@echo "$(COLOUR_GREEN)Running initial setup for local environment...$(COLOUR_NONE)"
	$(MAKE) create-ssl
	$(MAKE) first-use
	$(MAKE) start
	$(MAKE) migrate
	@echo "$(COLOUR_GREEN)Local setup complete.$(COLOUR_NONE)"

setup_local_force_rebuild:
	@echo "$(COLOUR_GREEN)Will run initial setup, followed by cache rebuild for local environment...$(COLOUR_NONE)"
	$(MAKE) setup_local
	@echo "$(COLOUR_GREEN)Manual cache rebuild (not using Celery task)...$(COLOUR_NONE)"
	$(MAKE) rebuild_cache
	@echo "$(COLOUR_GREEN)Cache rebuilt complete.$(COLOUR_NONE)"
