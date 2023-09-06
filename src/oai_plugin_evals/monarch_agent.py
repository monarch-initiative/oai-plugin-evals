##
## This example demonstrates a basic UtilityAgent that can call API endpoints and local methods
## 
##


from agent_smith_ai.utility_agent import UtilityAgent

import textwrap
import os
from typing import Any, Dict

# load environment variables from .env file
import dotenv
dotenv.load_dotenv()

## A UtilityAgent can call API endpoints and local methods
class MonarchAgent(UtilityAgent):

    def __init__(self, name):
        
        ## define a system message
        system_message = textwrap.dedent(f"""
            You are the Monarch Assistant, an AI-powered chatbot that can answer questions about data from the Monarch Initiative knowledge graph. 
            You can search for entities such as genes, diseases, and phenotypes by name to get the associated ontology identifier. 
            You can retrieve associations between entities via their identifiers. 
            Users may use synonyms such as 'illness' or 'symptom'. Do not assume the user is familiar with biomedical terminology. 
            Always add additional information such as lay descriptions of phenotypes. 
            If the user changes the show function call setting, do not make any further function calls immediately.
            IMPORTANT: Include markdown-formatted links to the Monarch Initiative for all results using the templates provided by function call responses.'.
            """).strip()
        
        super().__init__(name,                                             # Name of the agent
                         system_message,                                   # Openai system message
                         model = "gpt-3.5-turbo-0613",                     # Openai model name
                         openai_api_key = os.environ["OPENAI_API_KEY"],    # API key; will default to OPENAI_API_KEY env variable
                         auto_summarize_buffer_tokens = 500,               # Summarize and clear the history when fewer than this many tokens remains in the context window. Checked prior to each message sent to the model.
                         summarize_quietly = False,                        # If True, do not alert the user when a summarization occurs
                         max_tokens = None,                                # maximum number of tokens this agent can bank (default: None, no limit)
                         token_refill_rate = 10000.0 / 3600.0)             # number of tokens to add to the bank per second

        ## register some API endpoints (inherited from UtilityAgent)
        ## the openapi.json spec must be available at the spec_url:
        ##    callable endpoints must have a "description" and "operationId"
        ##    params can be in body or query, but must be fully specified
        self.register_api("monarch", 
                          spec_url = "https://oai-monarch-plugin.monarchinitiative.org/openapi.json", 
                          base_url = "https://oai-monarch-plugin.monarchinitiative.org",
                          callable_endpoints = ['search_entity', 
                                                'get_disease_gene_associations', 
                                                'get_disease_phenotype_associations', 
                                                'get_gene_disease_associations', 
                                                'get_gene_phenotype_associations', 
                                                'get_phenotype_gene_associations', 
                                                'get_phenotype_disease_associations'])

        ## the agent can also call local methods, but we have to register them
        self.register_callable_methods(['compute_entropy'])

    ## Callable methods should be type-annotated and well-documented with docstrings parsable by the docstring_parser library
    def compute_entropy(self, items: Dict[Any, int]) -> float:
        """Compute the information entropy of a given set of item counts.
        
        Args:
            items (str): A dictionary of items and their counts.
            
        Returns:
            The information entropy of the item counts.
        """
        from math import log2
        
        total = sum(items.values())
        return -sum([count / total * log2(count / total) for count in items.values()])


# agent = MonarchAgent("Monarch Assistant")
# question = "What genes are associated with Cystic Fibrosis?"

# ## agent.new_chat(question) may result in a series of Message objects (which may consist of a series of function-call messages,
# ## function-call responses, and other messages)
# ## by default, the system message and initial prompt question are not included in the output, but can be
# for message in agent.new_chat(question, yield_system_message = True, yield_prompt_message = True, author = "User"):
#     ## each Message object as the following attributes and defaults:
#         # role: str                                         // required, either "user", "assistant", or "function" (as used by OpenAI API)
#         # author: str = None                                // the name of the author of the message
#         # intended_recipient: str = None                    // the name of the intended recipient of the message
#         # is_function_call: bool = False                    // whether the message represents the model attemtpting to make a function call
#         # content: Optional[str] = None                     // the content of the message (as used by OpenAI API)
#         # func_name: Optional[str] = None                   // the function name the model is trying to call (if is_function_call is True)
#         # func_arguments: Optional[Dict[str, Any]] = None   // the function arguments the model is trying to pass (if is_function_call is True)
#         # finish_reason: Optional[str] = None               // (as used by the OpenAI API, largely ignorable)

#     ## the author and intended_recipient may be useful for multi-agent conversions or logging, they will typically be filled 
#     ## with agent names, "User", or the agent name and the function it is trying to call
#     print("\n\n", message.model_dump())

# ## agent.continue_chat(question) works just like .new_chat(), but doesn't allow including the system message
# question_followup = "What other diseases are associated with the first one you listed?"
# for message in agent.continue_chat(question_followup, yield_prompt_message = True, author = "User"):
#     print("\n\n", message.model_dump())

# question_followup = "What is the entropy of a standard tile set in Scrabble?"
# for message in agent.continue_chat(question_followup, yield_prompt_message = True, author = "User"):
#     print("\n\n", message.model_dump())