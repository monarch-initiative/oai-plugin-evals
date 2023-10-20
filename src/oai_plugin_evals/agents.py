from agent_smith_ai.utility_agent import UtilityAgent

import textwrap
import os
from typing import Any, Dict, List, Tuple

# load environment variables from .env file
import dotenv
dotenv.load_dotenv()

## BasicAnswerAgent just extends UtilityAgent to add a method for answering a question
## returning a simple string, rather than an iterator of messages. Everything else, including the constructor, is inherited
class BasicAnswerAgent(UtilityAgent):

    def answer(self, question: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Answer a question using the agent.

        Args:
            question (str): The question to answer

        Returns:
            str: The answer
        """
        messages = list(self.chat(question))
        agent_answer = messages[-1]
        context = [message.model_dump() for message in messages[:-1]]
        num_function_calls = sum([1 for message in context if message['role'] == 'function'])
        return agent_answer.content, num_function_calls, context



## A UtilityAgent can call API endpoints and local methods
class GeneAliasEvalAgent(UtilityAgent):

    def __init__(self):
        name = "Gene Alias Eval Agent GPT4"

        ## define a system message
        system_message = textwrap.dedent(f"""
            You are an evaluation agent, whose job it is to evaluate the performance of another agent, the Monarch Assistant.
            The Monarch Assistant an AI-powered chatbot that can answer questions about data from the Monarch Initiative knowledge graph.
            The Monarch Assistant will be asked to provide the official gene name for a given gene alias, your job is to score the answer by comparing the list of gene names mentioned by the agent to a gold standard answer.
            You are able to do this with the help of a function named compute_score, which takes a list of genes mentioned by the agent, and a single gold standard gene name, and returns a score between 0 and 1.
            """).strip()
        
        super().__init__(name,                                             # Name of the agent
                         system_message,                                   # Openai system message
                         model = "gpt-4-0613",                             # Openai model name
                         openai_api_key = os.environ["OPENAI_API_KEY"],    # API key; will default to OPENAI_API_KEY env variable
                         auto_summarize_buffer_tokens = 500,               # Summarize and clear the history when fewer than this many tokens remains in the context window. Checked prior to each message sent to the model.
                         summarize_quietly = False)
        
        self.register_callable_functions({"compute_score": self.compute_score})

    def compute_score(self, goldstandard: str, agent_answer: List[str]) -> float:
        """Compute a score between 0 and 1 based on the goldstandard and agent_answer lists of genes, as the percentage of gold standard genes mentioned by the agent.
        
        Args:
            goldstandard (str): Gold standard gene name
            agent_answer (List[str]): List of gene names mentioned by the agent
            
        Returns:
            float: Score between 0 and 1
        """
        goldstandard = set([goldstandard])
        count_intersection = len(set(goldstandard).intersection(agent_answer))
        count_union = len(set(goldstandard).union(agent_answer))
        jaccard = count_intersection / count_union
        return jaccard


    # uses the DiseaseGenesEvalAgent to evaluate the performance of another agent on the Disease Genes task
    def evaluate(self, question: str, goldstandard: str, agent_answer: str) -> Tuple[Dict[str, Any], float]:
        eval_message = f"""Considering the following question: {question}, score these two answers:

        gold-standard: {goldstandard}

        Monarch Assistant: {agent_answer}
        """

        # the eval agent is designed to call a function to do the evaluation, which takes the list of gold standard genes and a list of genes
        # mentioned by the monarch agent. Since we are starting a new chat with a question that can be answered by a function call,
        # the first message in the stream will be the function call and the second message will be the response.
        messages_iterator = self.chat(eval_message)
        
        # first message in the stream: the eval agent should be trying try to call the function
        function_call_message = next(messages_iterator)

        # it is possible that the eval agent doesn't decide to call the function, 
        # in which case there won't be two messages in the stream, or something else weird might happen
        # if there's a second message and it's a function response message, we can parse it to get the score
        # if we fail for some reason, set it to None
        # try:
        # second message in the stream: the function returns the score
        function_call_response = next(messages_iterator)
        # we don't need to continue the conversation further; saves us tokens on GPT-4!

        assert function_call_response.role == "function", "Second message in the stream was not a function response as expected"
        valuation = float(function_call_response.content)
        # except ValueError:
        #     function_call_response = None
        #     valuation = None
        
        # return all the info for provenance
        return {"function_call": function_call_message.model_dump(), "function_response": function_call_response.model_dump()}, valuation



## A UtilityAgent can call API endpoints and local methods
class DiseaseGenesEvalAgent(UtilityAgent):

    def __init__(self):
        name = "Disease Genes Eval Agent GPT4"

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
                         summarize_quietly = False)
        
        self.register_callable_functions({"compute_score": self.compute_score})

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


    # uses the DiseaseGenesEvalAgent to evaluate the performance of another agent on the Disease Genes task
    def evaluate(self, question: str, goldstandard: str, agent_answer: str) -> Tuple[Dict[str, Any], float]:
        eval_message = f"""Considering the following question: {question}, score these two answers:

        gold-standard: {goldstandard}

        Monarch Assistant: {agent_answer}
        """

        # the eval agent is designed to call a function to do the evaluation, which takes the list of gold standard genes and a list of genes
        # mentioned by the monarch agent. Since we are starting a new chat with a question that can be answered by a function call,
        # the first message in the stream will be the function call and the second message will be the response.
        messages_iterator = self.chat(eval_message)
        
        # first message in the stream: the eval agent should be trying try to call the function
        function_call_message = next(messages_iterator)

        # it is possible that the eval agent doesn't decide to call the function, 
        # in which case there won't be two messages in the stream, or something else weird might happen
        # if there's a second message and it's a function response message, we can parse it to get the score
        # if we fail for some reason, set it to None
        # try:
        # second message in the stream: the function returns the score
        function_call_response = next(messages_iterator)
        # we don't need to continue the conversation further; saves us tokens on GPT-4!

        assert function_call_response.role == "function", "Second message in the stream was not a function response as expected"
        valuation = float(function_call_response.content)
        # except ValueError:
        #     function_call_response = None
        #     valuation = None
        
        # return all the info for provenance
        return {"function_call": function_call_message.model_dump(), "function_response": function_call_response.model_dump()}, valuation




## A UtilityAgent can call API endpoints and local methods
class MonarchAgent4(BasicAnswerAgent):

    def __init__(self):
        name = "Monarch Assistant GPT4"
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
                         model = "gpt-4-0613",                             # Openai model name
                         openai_api_key = os.environ["OPENAI_API_KEY"],    # API key; will default to OPENAI_API_KEY env variable
                         auto_summarize_buffer_tokens = 500,               # Summarize and clear the history when fewer than this many tokens remains in the context window. Checked prior to each message sent to the model.
                         summarize_quietly = False)

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


## A UtilityAgent can call API endpoints and local methods
class MonarchAgent35(BasicAnswerAgent):

    def __init__(self):
        name = "Monarch Assistant GPT35"

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
                         model = "gpt-3.5-turbo-0613",                                    # Openai model name
                         openai_api_key = os.environ["OPENAI_API_KEY"],    # API key; will default to OPENAI_API_KEY env variable
                         auto_summarize_buffer_tokens = 500,               # Summarize and clear the history when fewer than this many tokens remains in the context window. Checked prior to each message sent to the model.
                         summarize_quietly = False)             

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


class DummyAgent4(BasicAnswerAgent):
    def __init__(self):
        name = "Dummy Agent GPT4"
        ## define a system message
        system_message = "You are a helpful assistant."

        super().__init__(name,                                             # Name of the agent
                         system_message,                                   # Openai system message
                         model = "gpt-4-0613",                                    # Openai model name
                         openai_api_key = os.environ["OPENAI_API_KEY"],    # API key; will default to OPENAI_API_KEY env variable
                         auto_summarize_buffer_tokens = 500,               # Summarize and clear the history when fewer than this many tokens remains in the context window. Checked prior to each message sent to the model.
                         summarize_quietly = False)             # number of tokens to add to the bank per second

class DummyAgent35(BasicAnswerAgent):
    def __init__(self):
        name = "Dummy Agent GPT35"
        ## define a system message
        system_message = "You are a helpful assistant."

        super().__init__(name,                                             # Name of the agent
                         system_message,                                   # Openai system message
                         model = "gpt-3.5-turbo-0613",                                    # Openai model name
                         openai_api_key = os.environ["OPENAI_API_KEY"],    # API key; will default to OPENAI_API_KEY env variable
                         auto_summarize_buffer_tokens = 500,               # Summarize and clear the history when fewer than this many tokens remains in the context window. Checked prior to each message sent to the model.
                         summarize_quietly = False)             # number of tokens to add to the bank per second
