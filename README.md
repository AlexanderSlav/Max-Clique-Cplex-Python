# Max-Clique-Cplex-Python


## Requirements
 - Python >= 3.6
 - pip install -r requirements.txt

## Evaluation on subset of DIMACS graphs
```bash
usage: max_clique_bnb_evaluator.py [-h] [--input_data_file INPUT_DATA_FILE]
                                   [--output_results_dump OUTPUT_RESULTS_DUMP]

optional arguments:
  -h, --help            show this help message and exit
  --input_data_file INPUT_DATA_FILE
                        path to file with input benchmarks data
  --output_results_dump OUTPUT_RESULTS_DUMP
                        path to output file

```

The sample of input data file.

```text
GraphName,CorrectMaxClique,Level
johnson8-2-4.clq,4,E
```
