##
## This example demonstrates a basic UtilityAgent that can call API endpoints and local methods
## 
##


from agent_smith_ai.utility_agent import UtilityAgent

import textwrap
import os
from typing import Any, Dict, List

# load environment variables from .env file
import dotenv
dotenv.load_dotenv()

## A UtilityAgent can call API endpoints and local methods
class DiseaseGenesEvalAgent(UtilityAgent):

    def __init__(self, name):
        
        ## define a system message
        system_message = textwrap.dedent(f"""
            You are an evaluation agent, whose job it is to evaluate the performance of another agent, the Monarch Assistant.
            The Monarch Assistant an AI-powered chatbot that can answer questions about data from the Monarch Initiative knowledge graph.
            The Monarch Assistant will be asked which genes are associated with a given disease, your job is to compute what percentage of those mentioned by the agent are present in a gold-standard dataset.
            You are able to do this with the help of a function named compute_score, which takes two lists of genes as input and returns a score between 0 and 1.
            """).strip()
        
        super().__init__(name,                                             # Name of the agent
                         system_message,                                   # Openai system message
                         model = "gpt-4-0613",                             # Openai model name
                         openai_api_key = os.environ["OPENAI_API_KEY"],    # API key; will default to OPENAI_API_KEY env variable
                         auto_summarize_buffer_tokens = 500,               # Summarize and clear the history when fewer than this many tokens remains in the context window. Checked prior to each message sent to the model.
                         summarize_quietly = False,                        # If True, do not alert the user when a summarization occurs
                         max_tokens = None,                                # maximum number of tokens this agent can bank (default: None, no limit)
                         token_refill_rate = 10000.0 / 3600.0)             # number of tokens to add to the bank per second

        self.register_callable_methods(["compute_score"])

    def compute_score(self, goldstandard: List[str], agent_answer: List[str]) -> float:
        """Compute a score between 0 and 1 based on the goldstandard and agent_answer lists of genes, as the percentage of gold standard genes mentioned by the agent.
        
        Args:
            goldstandard (List[str]): List of genes in the gold standard
            agent_answer (List[str]): List of genes mentioned by the agent
            
        Returns:
            float: Score between 0 and 1
        """
        count_intersection = len(set(goldstandard).intersection(agent_answer))
        return count_intersection / len(goldstandard)
