SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: run-tests, report

run-tests:
	poetry run python3 src/oai_plugin_evals/main.py

docs/index.html: r_viz/monarch_assistant_evals.Rmd r_viz/monarch_assistant_evals.html
	make -C r_viz monarch_assistant_evals.html
	cp r_viz/monarch_assistant_evals.html docs/index.html