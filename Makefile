deps:
	poetry install

dev: deps
	cd app && poetry run python main.py

codecarbon-monitor:
	poetry run codecarbon monitor --no-api

codecarbon-report:
	poetry run carbonboard --filepath="app/emissions.csv" --port=3333

lint: 
	poetry run ruff format
