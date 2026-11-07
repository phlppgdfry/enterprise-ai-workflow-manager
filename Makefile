.PHONY: test run install help

help:
	@echo "Beschikbare opdrachten:"
	@echo "  make install  - Installeer vereiste Python dependencies"
	@echo "  make test     - Voer de geautomatiseerde testsuite uit"
	@echo "  make run      - Start de lokale FastAPI server op poort 8000"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

run:
	python3 main.py
