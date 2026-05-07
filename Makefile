.PHONY: setup check format lint typecheck test deploy run deploy-run all

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

deploy:
	./scripts/deploy.sh

run:
	./scripts/run.sh

deploy-run:
	./scripts/deploy-run.sh

all: check
