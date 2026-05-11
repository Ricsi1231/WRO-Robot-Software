.PHONY: setup check format lint typecheck test coverage deploy run deploy-run all

setup:
	./scripts/setup.sh

check:
	./scripts/check.sh

format:
	./scripts/format.sh

lint:
	ruff check .

typecheck:
	mypy wro/ main.py calibrate.py component_tests

test:
	pytest

coverage:
	pytest --cov --cov-report=term-missing --cov-report=xml

deploy:
	./scripts/deploy.sh

run:
	./scripts/run.sh

deploy-run:
	./scripts/deploy-run.sh

all: check
