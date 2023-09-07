"""Main python file."""
from agent_smith_ai.utility_agent import UtilityAgent
from .monarch_agent import MonarchAgent
from .disease_genes_eval_agent import DiseaseGenesEvalAgent
import pandas as pd
import os
import pprint
import json

pp = pprint.PrettyPrinter(indent=4)


# uses the DiseaseGenesEvalAgent to evaluate the performance of another agent on the Disease Genes task
def eval_disease_genes_answer(question: str, goldstandard: str, agent_answer: str):
    eval_agent = DiseaseGenesEvalAgent("Disease Genes Eval Agent") # uses GPT-4 for evaluation
    eval_message = f"""Considering the following question: {question}, score these two answers:

    gold-standard: {goldstandard}

    Monarch Assistant: {agent_answer}
    """

    # the eval agent is designed to call a function to do the evaluation, which takes the list of gold standard genes and a list of genes
    # mentioned by the monarch agent. Since we are starting a new chat with a question that can be answered by a function call,
    # the first message in the stream will be the function call and the second message will be the response.
    messages_iterator = eval_agent.new_chat(eval_message)
    
    # first message in the stream: the eval agent should be trying try to call the function
    function_call_message = next(messages_iterator)

    # it is possible that the eval agent doesn't decide to call the function, 
    # in which case there won't be two messages in the stream, or something else weird might happen
    # if there's a second message and it's a function response message, we can parse it to get the score
    # if we fail for some reason, set it to None
    try:
        # second message in the stream: the function returns the score
        function_call_response = next(messages_iterator)
        # we don't need to continue the conversation further; saves us tokens on GPT-4!

        assert function_call_response.role == "function", "Second message in the stream was not a function response as expected"
        valuation = float(function_call_response.content)
    except ValueError:
        function_call_response = None
        valuation = None
    
    # return all the info for provenance
    return function_call_message.model_dump(), function_call_response.model_dump(), valuation



def main():
    current_location = os.path.dirname(os.path.realpath(__file__))
    gene_turing = pd.read_csv(os.path.join(current_location, "datasets/geneturing/qa.csv"), header=0)

    # select "Gene disease association" questions for now
    gene_turing = gene_turing[gene_turing['Module'] == 'Gene disease association']


    results = []
    for row_index in range(5): #range(len(gene_turing)):
        module = gene_turing.iloc[row_index]['Module']
        question = gene_turing.iloc[row_index]['Question']
        goldstandard = gene_turing.iloc[row_index]['Goldstandard']
        print(f"Module: {module}, Question: {question}, Goldstandard: {goldstandard}")
       
        # define a monarch agent to answer the question
        monarch_agent = MonarchAgent("Monarch Assistant")

        # get the answer from the agent. it will make multiple function calls to the monarch API,
        # with the final answer being the last message in the stream
        monarch_messages = list(monarch_agent.new_chat(question))
        monarch_messages_dict = [message.model_dump() for message in monarch_messages]
        monarch_agent_answer = monarch_messages[-1]
        print("Monarch agent answer: ", monarch_agent_answer.content)

        # evaluate the answer
        monarch_eval_message, monarch_eval_response, monarch_eval_valuation = eval_disease_genes_answer(question, goldstandard, monarch_agent_answer.content)

        ## Same, but now with a dummy agent without monarch backing
        dummy_agent = UtilityAgent("Assistant", system_message = "You are a helpful assistant.", model = "gpt-3.5-turbo-0613")
        dummy_messages = list(dummy_agent.new_chat(question))
        dummy_messages_dict = [message.model_dump() for message in dummy_messages]
        dummy_agent_answer = dummy_messages[-1]
        print("Dummy agent answer: ", dummy_agent_answer.content)

        # evaluate the answer
        dummy_eval_message, dummy_eval_response, dummy_eval_valuation = eval_disease_genes_answer(question, goldstandard, dummy_agent_answer.content)


        result = {'module': module, 
                  'question': question, 
                  'goldstandard': goldstandard,
                  'monarch_agent': {
                      'agent_answer': monarch_agent_answer.content, 
                      'conversation': monarch_messages_dict, 
                      'eval_message': monarch_eval_message, 
                      'eval_response': monarch_eval_response,
                      'eval_valuation': monarch_eval_valuation
                    },
                  'dummy_agent': {
                      'agent_answer': dummy_agent_answer.content, 
                      'conversation': dummy_messages_dict, 
                      'eval_message': dummy_eval_message, 
                      'eval_response': dummy_eval_response,
                      'eval_valuation': dummy_eval_valuation
                    }
                  }
       
        results.append(result)
        pp.pprint(result)
        
    # write test_results.json file
    with open(os.path.join(current_location, "test_results.json"), 'w') as f:
        json.dump(results, f, indent=4)



if __name__ == "__main__":
    main()