GALAXY_RELEASE_IMAGE ?= galaxy
GALAXY_RELEASE_TAG ?= latest

VENV_BIN=/var/lib/galaxy/venv/bin
DOCKER_COMPOSE=docker-compose -p galaxy -f ./scripts/docker/dev/compose.yml

.PHONY: help
help:
	@echo "Prints help"

# ---------------------------------------------------------
# Common targets
# ---------------------------------------------------------

.PHONY: runserver
runserver:
	python manage.py runserver 0.0.0.0:8888

.PHONY: celery
celery:
	python manage.py celeryd -B --autoreload -Q 'celery,import_tasks,login_tasks,admin_tasks,user_tasks,star_tasks'

.PHONY: ng_server
ng_server:
	cd /galaxy/galaxyui; ng serve --host '0.0.0.0' --port '8000' --poll '5000' --watch --live-reload --progress=false ----proxy-config proxy.conf.js

.PHONY: waitenv
waitenv:
	@echo "Waiting for services to start..."
	python ./manage.py waitenv

.PHONY: migrate
migrate:
	@echo "Run migrations"
	python ./manage.py migrate --noinput

.PHONY: collectstatic
collectstatic:
	python manage.py collectstatic --noinput --clear

.PHONY: clean
clean:
	rm -rfv dist build *.egg-info
	rm -rfv rpm-build debian deb-build
	rm -rfv galaxyui/dist
	find . -type f -name "*.pyc" -delete

.PHONY: createsuperuser
	@echo Create super user
	${VENV_BIN}/python ./manage.py createsuperuser

# ---------------------------------------------------------
# Build targets
# ---------------------------------------------------------

.PHONY: build/yarn
build/yarn:
	cd galaxyui; yarn install

.PHONY: build/static
build/static:
	cd galaxyui; ng build --prod --source-map

.PHONY: build/dist
build/dist: build/static
	python setup.py clean bdist_wheel
	GALAXY_VERSION=$$(python setup.py --version) \
		&& ln -sf galaxy-$$GALAXY_VERSION-py2-none-any.whl dist/galaxy.whl

.PHONY: build/docker-dev
build/docker-dev:
	docker build --rm -t galaxy-dev -f scripts/docker/dev/Dockerfile .

.PHONY: build/release
build/release:
	@echo "Building base container..."
	@docker build -t galaxy-base:latest \
		-f scripts/docker/release/Dockerfile.base .
	@echo "Building build container..."
	@docker build -t galaxy-build:latest \
		-f scripts/docker/release/Dockerfile.build .
	@echo "Building galaxy container..."
	@docker build -t $(GALAXY_RELEASE_IMAGE):$(GALAXY_RELEASE_TAG) \
		-f scripts/docker/release/Dockerfile .
	@echo "Building static container..."
	@docker build -t $(GALAXY_RELEASE_IMAGE)-static:$(GALAXY_RELEASE_TAG) \
		-f scripts/docker/release/Dockerfile.static .

# ---------------------------------------------------------
# Test targets
# ---------------------------------------------------------

.PHONY: test/flake8
test/flake8:
	flake8 galaxy

.PHONY: test/jslint
test/jslint:
	cd galaxyui; ng lint

# for some reason yarn won't add prettier to /usr/local/bin
.PHONY: test/prettier
test/prettier:
	@echo "Checking formatting..."
	@echo "If this fails, run make dev/prettier locally to format your code"
	cd galaxyui; ./node_modules/.bin/prettier -l "{src/**/*.ts, src/**/*.less}"

# ---------------------------------------------------------
# Docker targets
# ---------------------------------------------------------

.PHONY: docker/test-flake8
docker/test-flake8:
	docker run --rm -i -t -v $(CURDIR):/galaxy galaxy-dev:latest make test/flake8

# ---------------------------------------------------------
# Development targets
# ---------------------------------------------------------

.PHONY: dev/build
dev/build: build/docker-dev

.PHONY: dev/createsuperuser
dev/createsuperuser:
	@echo "Create Superuser"
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py createsuperuser

.PHONY: dev/migrate
dev/migrate:
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py migrate --noinput

.PHONY: dev/makemigrations
dev/makemigrations:
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py makemigrations

.PHONY: dev/log
dev/log:
	@$(DOCKER_COMPOSE) logs --tail 100 galaxy

.PHONY: dev/logf
dev/logf:
	@$(DOCKER_COMPOSE) logs -f galaxy

.PHONY: dev/flake8
dev/flake8:
	@echo "Running flake8"
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/flake8 galaxy

.PHONY: dev/jslint
dev/jslint:
	@echo "Linting Javascript..."
	@$(DOCKER_COMPOSE) exec galaxy bash -c 'cd galaxyui; ng lint'

# for some reason yarn won't add prettier to /usr/local/bin
.PHONY: dev/prettier
dev/prettier:
	@echo "Running prettier..."
	@$(DOCKER_COMPOSE) exec galaxy bash -c 'cd galaxyui; ./node_modules/.bin/prettier --write "{src/**/*.ts, src/**/*.less}"'

.PHONY: dev/shellcheck
dev/shellcheck:
	@$(DOCKER_COMPOSE) exec galaxy bash -c '\
		find ./scripts -name *.sh | xargs shellcheck'

.PHONY: dev/test
dev/test:
	@echo "Running tests"
# TODO:  Revert to $(DOCKER_COMPOSE)
# Currently `docker exec` offers -e option for setting Env variables, and `docker-compose exec` does not.
# Setting the postgres connetion string to use postgres user, to have authority to create and destroy the test database.
	@docker exec -e GALAXY_DB_URL=postgres://postgres:postgres@postgres:5432/galaxy galaxy_galaxy_1 bash -c 'source $(VENV_BIN)/activate; pytest galaxy'

.PHONY: dev/waitenv
dev/waitenv:
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/python ./manage.py waitenv

.PHONY: dev/up
dev/up:
	$(DOCKER_COMPOSE) up

.PHONY: dev/pip_install
dev/pip_install:
	@$(DOCKER_COMPOSE) exec galaxy $(VENV_BIN)/pip install -r requirements.txt

# Start all containers detached
.PHONY: dev/up_detached
dev/up_detached:
	$(DOCKER_COMPOSE) up -d

.PHONY: dev/up_tmux
dev/up_tmux:
	# Run before dev/tmux to start containers detached and no processes running in the galaxy container.
	@TMUX=1 $(DOCKER_COMPOSE) up -d

.PHONY: dev/down
dev/down:
	$(DOCKER_COMPOSE) down

.PHONY: dev/restart
dev/restart:
	# Restart one or more services
	$(DOCKER_COMPOSE) restart $(filter-out $@,$(MAKECMDGOALS))

.PHONY: dev/stop
dev/stop:
	# Stop one or more services
	$(DOCKER_COMPOSE) stop $(filter-out $@,$(MAKECMDGOALS))

.PHONY: dev/rm
dev/rm:
	# Remove services
	$(DOCKER_COMPOSE) stop
	$(DOCKER_COMPOSE) rm -f

# Create the tmux session. Do NOT call directly. Use dev/tmux or dev/tmuxcc instead.
.PHONY: dev/tmux_noattach
dev/tmux_noattach:
	tmux new-session -d -s galaxy -n galaxy \; \
		 set-option -g allow-rename off \; \
		 send-keys "scripts/docker/dev/entrypoint.sh make runserver" Enter \; \
		 new-window -n celery \; \
		 send-keys "scripts/docker/dev/entrypoint.sh make celery" Enter \; \
		 new-window -n ng \; \
		 send-keys "make ng_server" Enter

.PHONY: dev/tmux
dev/tmux:
	# Connect to the galaxy container, start processes, and pipe stdout/stderr through a tmux session
	$(DOCKER_COMPOSE) exec galaxy script /dev/null -q -c 'make dev/tmux_noattach; tmux -2 attach-session -t galaxy'

.PHONY: dev/tmuxcc
dev/tmuxcc: dev/tmux_noattach
	# Same as above using iTerm's built-in tmux support
	$(DOCKER_COMPOSE) exec galaxy bash -c 'make dev/tmux_noattach; tmux -2 -CC attach-session -t galaxy'

.PHONY: dev/export-test-data
export-test-data:
	@echo Export data to test-data/role_data.dmp.gz
	$(DOCKER_COMPOSE) /galaxy/test-data/export.sh

.PHONY: dev/import-test-data
import_test_data:
	@echo Import data from test-data/role_data.dmp.gz
	$(DOCKER_COMPOSE) /galaxy/test-data/import.sh

.PHONY: dev/refresh-role-counts
refresh-role-counts:
	@echo Refresh role counts
	$(DOCKER_COMPOSE) $(VENV_BIN)/python ./manage.py refresh_role_counts

%:
	@:
