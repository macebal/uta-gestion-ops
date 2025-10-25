.PHONY: sync run package clean

sync:
	uv sync --all-groups

run: sync
	uv run main.py

package: clean sync
	uv run pyinstaller uta-gestion-ops.spec

clean:
	rm -rf build dist __pycache__ src/__pycache__

