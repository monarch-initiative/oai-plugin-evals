# oai-plugin-evals

Evaluations for the Monarch OpenAI Plugin/Monarch Assistant against benchmarks. Work in progress: set OPENAI_API_KEY in `.env`, and
run `make`. Currently only tests the disease -> gene association test from the GeneTuring benchmark, using an automated evaluation of agent answers provided by a `DiseaseGenesEvalAgent`.

Current early test evaluations are in [1src/oai_plugin_evals/test_results.json1](https://raw.githubusercontent.com/monarch-initiative/oai-plugin-evals/main/src/oai_plugin_evals/test_results.json), browse with your favorite JSON-friendly viewer.

# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [monarch-project-template](https://github.com/monarch-initiative/monarch-project-template) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).