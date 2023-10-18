SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: tests

run-tests:
	poetry run python3 src/oai_plugin_evals/main.py