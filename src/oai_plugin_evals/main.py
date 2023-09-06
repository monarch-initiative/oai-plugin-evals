"""Main python file."""
from .monarch_agent import MonarchAgent
import pandas as pd
import os

def main():
    current_location = os.path.dirname(os.path.realpath(__file__))
    gene_turing = pd.read_csv(os.path.join(current_location, "datasets/geneturing/qa.csv"), header=0)
    print(gene_turing.head())

if __name__ == "__main__":
    main()