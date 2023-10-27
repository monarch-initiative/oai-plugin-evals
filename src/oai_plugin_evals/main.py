"""Main python file."""
from oai_plugin_evals.trial import Trial
from oai_plugin_evals.agents import *
import os
import json
import sys


def load_eval_data():
    run_location = os.getcwd()
    all_data = json.load(open(run_location + "/datasets/geneturing/geneturing_converted.json"))
    # only keep entries where Model is New Bing, since we just want the questions not all the other model answers for now
    # we also only want the fields for Question, Module, and Goldstandard
    all_data = [{k: v for k, v in d.items() if k in ['Question', 'Module', 'Goldstandard']} for d in all_data if d['Model'] == 'New Bing']

    return all_data

sys.stderr.write("Loading eval data\n")
all_data = load_eval_data()

model_classes_to_test = [MonarchAgent35, DummyAgent35, MonarchAgent4, DummyAgent4]
trials = []

sys.stderr.write("Creating trials\n")
# Modules:
# [ ] "Gene alias", "Question": "What is the official gene symbol of LMP10?", "Goldstandard": "PSMB10"
gene_alias_data = [d for d in all_data if d['Module'] == 'Gene alias']
for model_class in model_classes_to_test:
    for example in gene_alias_data:
        trials.append(Trial(example['Module'], example['Question'], example['Goldstandard'], model_class, GeneAliasEvalAgent, results_location = "./results"))

# [ ] "Gene disease association", "Question": "What are genes related to Distal renal tubular acidosis?", "Goldstandard": "SLC4A1, ATP6V0A4"
gene_disease_association_data = [d for d in all_data if d['Module'] == 'Gene disease association']
for model_class in model_classes_to_test:
    for example in gene_disease_association_data:
        trials.append(Trial(example['Module'], example['Question'], example['Goldstandard'], model_class, DiseaseGenesEvalAgent, results_location = "./results"))

# [ ] "Gene location", "Question": "Which chromosome is RP11-17A4.3 gene located on human genome?", "Goldstandard": "chr8"
# [ ] "Gene ontology", "Question": "What is the enriched gene ontology term associated with FMR1, FBXL2, TMEM41B, PHB1, DDX56?", "Goldstandard": "modulation by host of viral rna genome replication"
# [ ] "Human genome DNA aligment", "Question": "Align the DNA sequence to the human genome:TGAGAGCACAGTGGTGAGGAGGACCCACATGCCTCCTATCCTTCATAGGAGGAGAAAGGCACAAACCAGAAAACCCCCCCAACACACACACACATACACAT", "Goldstandard": "chr1:234883857-234883957"
# [ ] "Multi-species DNA aligment", "Question": "Which organism does the DNA sequence come from:TTCAATTCTCTGTAGGCAAGGATGGCTCATCACCATTATCACCCTGACGAGACTTAGAAACACCACGGAGACACACCTCTGGGCACGAGTGTTATGGTGTTT", "Goldstandard": "rat"
# [ ] "Gene name conversion", "Question": "Convert ENSG00000205403 to official gene symbol.", "Goldstandard": "CFI"
# [ ] "Gene name extraction", "Question": "What are the gene and protein names in the sentence: Differences were not found in colons by SEM.?", "Goldstandard": "No gene"
#         "Gene name extraction", "Question": "What are the gene and protein names in the sentence: The H5 mutants were: DH5 (all amino acids in D configuration) and H5F (where all His are replaced by Phe at positions 3, 7, 8, 15, 18, 19, 21).?", "Goldstandard": "H5 mutants, DH5, H5F"
# [ ] "Protein-coding genes", "Question": "Is AMD1P4 a protein-coding gene?", "Goldstandard": null
#         "Protein-coding genes", "Question": "Is NODAL a protein-coding gene?", "Goldstandard": "TRUE"
# [ ] "Gene SNP association", "Question": "Which gene is SNP rs1217074595 associated with?", "Goldstandard": "LINC01270"
# [ ] "SNP location", "Question": "Which chromosome does SNP rs545148486 locate on human genome?", "Goldstandard": "chr16"
# [ ] "TF regulation", "Question": "Does transcription factor ETV4 activate or repress gene ERBB2?", "Goldstandard": "Repression"

sys.stderr.write("Starting trials\n")
for trial in trials:
    trial.run()
