import hashlib
import json
import os
import pprint
import re
import sys
from typing import List, Dict, Any, Tuple
from oai_plugin_evals.agents import *

pp = pprint.PrettyPrinter(indent=4)

## A trial represents a single question, answered by a single agent, and evaluated by an evaluator agent type against a gold standard answer.
## The trial object takes care of writing the results to a file, and can be used to load the results from a file.
## This provides a caching mechanism for answering and evaluation due to it's cost, but we can also choose to re-run
## the trial if necessary, for example if agent or evalation logic changes. 
## The Trial can also handle re-trying on error.
class Trial:
    def __init__(self, module: str, question: str, goldstandard: str, agent_class: BasicAnswerAgent, evaluator_class: UtilityAgent, results_location: str = None):
        self.module = module
        self.question = question
        self.agent_class = agent_class
        self.evaluator_class = evaluator_class
        self.goldstandard = goldstandard
        self.results_location = results_location
        # a short alphanumeric hash of the question and module, e.g. a45cd7b1
        # fyi python's default hash() is non-deterministic across runs since 3.3, which is obnoxious
        def deterministic_hash(s):
            return hashlib.sha256(s.encode()).hexdigest()

        self.question_id = deterministic_hash(question + module)[-8:]

        agent_name = self.agent_class().name
        agent_name = re.subn("[^A-Za-z0-9]+", "_", agent_name.lower())[0]
        module = re.subn("[^A-Za-z0-9]+", "_", module.lower())[0]
        self.cache_file = self.results_location + f"/trial-{module}-{agent_name}-{self.question_id}.json"

    ## TODO: I don't actually know if the we'll ever see the error, as I think errors are captured by the agent and evaluator
    ## and returned as a message. Might need to update agent-smith for this, to provide an option for what to do with errors (e.g. report in message, retry, or throw)
    def run(self, retry_on_error: bool = True, clear_cache_file = False):
        # if the results location folder doesn't exist, create it
        if not os.path.exists(self.results_location):
            os.makedirs(self.results_location)

        # if the cache file exists, and we're not clearing it, load the results from the cache file
        if os.path.exists(self.cache_file) and not clear_cache_file:
            with open(self.cache_file, 'r') as f:
                sys.stderr.write(f"Loading results from cache file {self.cache_file}\n")
                results = json.load(f)
        else:
            sys.stderr.write(f"Cache file not found. Running trial for question {self.question_id}\n")
            results = self.run_trial(retry_on_error = retry_on_error)
            with open(self.cache_file, 'w') as f:
                json.dump(results, f, indent=4)

        result_pretty = pp.pformat(results)
        sys.stderr.write(f"Trial results: {result_pretty}\n")

        return results
    
    def run_trial(self, retry_on_error: bool = False):
        # run the agent
        sys.stderr.write(f"Running agent {self.agent_class().name} on question {self.question_id}\n")
        agent = self.agent_class()
        agent_answer, agent_answer_num_function_calls, agent_answer_provenance = agent.answer(self.question)
        agent_name = agent.name

        # evaluate the answer
        try:
            sys.stderr.write(f"Evaluating answer for question {self.question_id}\n")
            eval_agent = self.evaluator_class()
            res = eval_agent.evaluate(self.question, self.goldstandard, agent_answer)

            eval_provenance, eval_valuation = res
        except Exception as e:
            if retry_on_error:
                sys.stderr.write(f"Error evaluating answer: {e}. Retrying...")
                return self.run_trial()
            else:
                raise e

        result = {
            'module': self.module, 
            'question': self.question, 
            'goldstandard': self.goldstandard,
            'agent_name': agent_name,
            'agent_answer': agent_answer, 
            'agent_answer_num_function_calls': agent_answer_num_function_calls,
            'agent_answer_provenance': agent_answer_provenance,
            'eval_provenance': eval_provenance, 
            'eval_valuation': eval_valuation
        }

        return result

