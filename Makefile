.PHONY: sync run package clean create-test-data pretty

sync:
	uv sync --all-groups

run: sync
	uv run main.py

package: clean sync
	uv run pyinstaller uta-gestion-ops.spec

clean:
	rm -rf build dist __pycache__ src/__pycache__

create-test-data: sync
	uv run python scripts/load_test_data.py

pretty: sync
	uv run ruff check --fix .
	uv run ruff format .

test: sync
	uv run pytest