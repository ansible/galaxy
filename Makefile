GALAXY_RELEASE_IMAGE ?= galaxy
GALAXY_RELEASE_TAG ?= latest

GALAXY_VENV=/usr/share/galaxy/venv
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
	python manage.py celery worker --beat -Q 'celery,import_tasks,login_tasks,admin_tasks,user_tasks,star_tasks'

.PHONY: ng_server
ng_server:
	cd /galaxy/galaxyui; ng serve --disable-host-check --host '0.0.0.0' --port '8000' --poll '5000' --watch --live-reload --progress=false ----proxy-config proxy.conf.js

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
	python ./manage.py createsuperuser

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

.PHONY: test
test:
	@pytest galaxy \
	--cov galaxy \
	--cov-report xml \
	--cov-report term \
	--cov-report html \
	--cov-config setup.cfg \

.PHONY: test/changed
test/changed:
	@git status | grep -e '   .*test' | cut -d: -f2 | xargs pytest -s -vvv --reuse-db

.PHONY: test/flake8
test/flake8:
	flake8 galaxy

.PHONY: test/yamllint
test/yamllint:
	yamllint -s .

.PHONY: test/jslint
test/jslint:
	cd galaxyui; ng lint

# for some reason yarn won't add prettier to /usr/local/bin
.PHONY: test/prettier
test/prettier:
	@echo "Checking formatting..."
	@echo "If this fails, run make dev/prettier locally to format your code"
	cd galaxyui; ./node_modules/.bin/prettier -l "src/**/*.less" "src/**/*.ts"

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
	@$(DOCKER_COMPOSE) exec galaxy $(GALAXY_VENV)/bin/python ./manage.py createsuperuser

.PHONY: dev/migrate
dev/migrate:
	@$(DOCKER_COMPOSE) exec galaxy $(GALAXY_VENV)/bin/python ./manage.py migrate --noinput

.PHONY: dev/makemigrations
dev/makemigrations:
	@$(DOCKER_COMPOSE) exec galaxy $(GALAXY_VENV)/bin/python ./manage.py makemigrations

.PHONY: dev/checkmigrations
dev/checkmigrations:
	@$(DOCKER_COMPOSE) exec galaxy $(GALAXY_VENV)/bin/python ./manage.py makemigrations --dry-run --check

.PHONY: dev/compile-reqs
dev/compile-reqs:
	pip-compile -o requirements/requirements.txt requirements/requirements.in
	pip-compile -o requirements/dev-requirements.txt requirements/dev-requirements.in

.PHONY: dev/log
dev/log:
	@$(DOCKER_COMPOSE) logs --tail 100 galaxy

.PHONY: dev/logf
dev/logf:
	@$(DOCKER_COMPOSE) logs -f galaxy

.PHONY: dev/flake8
dev/flake8:
	@echo "Running flake8"
	@$(DOCKER_COMPOSE) exec galaxy $(GALAXY_VENV)/bin/flake8 galaxy

.PHONY: dev/jslint
dev/jslint:
	@echo "Linting Javascript..."
	@$(DOCKER_COMPOSE) exec galaxy bash -c 'cd galaxyui; ng lint'

# for some reason yarn won't add prettier to /usr/local/bin
.PHONY: dev/prettier
dev/prettier:
	@echo "Running prettier..."
	@$(DOCKER_COMPOSE) exec galaxy bash -c 'cd galaxyui; ./node_modules/.bin/prettier --write "src/**/*.less" "src/**/*.ts" "src/**/*.tsx"'

.PHONY: dev/shellcheck
dev/shellcheck:
	@$(DOCKER_COMPOSE) exec galaxy bash -c '\
		find ./scripts -name *.sh | xargs shellcheck'

.PHONY: dev/test
dev/test:
	@echo "Running tests"
# TODO: Revert to $(GALAXY_VENV)/bin/python. Some tests (flake8 and yamllint) require
# tools on $PATH, this cannot be chieved with just $(GALAXY_VENV)/bin/python command.
# So virtual environment must be activated in order to expose these utilities.
# TODO: Since app is isolated in container already, it's probably acceptable to
# get rid of virtual environment and install python packages in system dirs.
# Other option are:
# - install side packages globally or
# - call tools using python api instead of shell commands.
	@$(DOCKER_COMPOSE) exec galaxy bash -c '\
		source $(GALAXY_VENV)/bin/activate; \
		export DJANGO_SETTINGS_MODULE=galaxy.settings.testing; \
		pytest galaxy \
		--cov galaxy \
		--cov-report xml \
		--cov-report term \
		--cov-report html \
		--cov-config setup.cfg \
		'

.PHONY: dev/test/changed
dev/test/changed:
	@echo "Running changed tests"
	@$(DOCKER_COMPOSE) exec galaxy bash -c '\
		source $(GALAXY_VENV)/bin/activate; \
		export DJANGO_SETTINGS_MODULE="galaxy.settings.testing"; \
		git status --untracked-files=no | grep "galaxy\/.*test" | cut -d: -f2 > /tmp/tests_changed; \
		if [[ -s /tmp/tests_changed ]]; then \
				cat /tmp/tests_changed | xargs pytest -s -vvv --reuse-db \
		;else \
				echo "No test changes found. make dev/test to run all tests." \
		;fi \
		'

.PHONY: dev/waitenv
dev/waitenv:
	@$(DOCKER_COMPOSE) exec galaxy $(GALAXY_VENV)/bin/python ./manage.py waitenv

.PHONY: dev/pip_install
dev/pip_install:
	@$(DOCKER_COMPOSE) exec galaxy $(GALAXY_VENV)/bin/pip install -r requirements.txt

# Start all containers detached
.PHONY: dev/up
dev/up:
	$(DOCKER_COMPOSE) up

.PHONY: dev/up_detached
dev/up_detached:
	$(DOCKER_COMPOSE) up -d

.PHONY: dev/attach
dev/attach:
	# Run before dev/tmux to start containers detached and no processes running in the galaxy container.
	$(DOCKER_COMPOSE) exec galaxy tmux attach

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
	$(DOCKER_COMPOSE) $(GALAXY_VENV)/bin/python ./manage.py refresh_role_counts

.PHONY: dev/setup-metrics
dev/setup-metrics:
	cd scripts/metrics-setup-playbook; ansible-playbook setup.yml

%:
	@:
