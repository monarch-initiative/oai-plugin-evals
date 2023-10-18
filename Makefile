SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: tests

eval-gene-disease:
	poetry run eval-gene-disease