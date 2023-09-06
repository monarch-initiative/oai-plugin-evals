SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: tests

tests:
	poetry run main