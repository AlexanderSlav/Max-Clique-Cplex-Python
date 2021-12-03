# Max-Clique-Cplex-Python


### Requirements
 - Install Cplex for Python
 - Python >= 3.6
 - pip install -r requirements.txt

### Evaluation on subset of DIMACS graphs
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

### Machine Characteristics Info
All graphs were evaluated on the machine with the following characteristics:

**RAM** - 64GB


![](imgs/machine_info.png)

## Evaluation Results

### BnB
### Easy graphs

|Graph Name   |Correct Max Clique|Graph Complexity|Found Max Clique|Is Clique|Consumed Time(seconds)|
|-------------|------------------|----------------|----------------|---------|-------------|
|johnson8-2-4 |4                 |E               |4               |True     |0.244        |
|johnson16-2-4|8                 |E               |8               |True     |41.034       |
|MANN_a9      |16                |E               |16              |True     |**1.128**        |
|keller4      |11                |E               |11              |True     |**175.136**      |
|hamming8-4   |16                |E               |16              |True     |**37.038**       |

### Meduim graphs

|Graph Name   |Correct Max Clique|Graph Complexity|Found Max Clique|Is Clique|Consumed Time(seconds)|
|-------------|------------------|----------------|----------------|---------|-------------|
|brock200_2 |12                |M               |12               |True     |**244.075**         |
|brock200_3 |15                 |M                 |15               |True     |**484.801**       |
|brock200_4      |17               |M                |17              |True     |2680.945        |
|C125.9    |34               |M                 |34              |True     |493.235      |
|gen200_p0.9_44  |44                |M                  |44              |True     |**2218.3**       |
|gen200_p0.9_45  |55                |M                  |55              |True     |**34.521**      |


### BnC
### Easy graphs

|Graph Name   |Correct Max Clique|Graph Complexity|Found Max Clique|Is Clique|Consumed Time(seconds)|
|-------------|------------------|----------------|----------------|---------|-------------|
|johnson8-2-4 |4                 |E               |4               |True     |0.272       |
|johnson16-2-4|8                 |E               |8               |True     |**7.882**      |
|MANN_a9      |16                |E               |16              |True     |2.571       |
|keller4      |11                |E               |11              |True     |248.607      |
|hamming8-4   |16                |E               |16              |True     |139.144      |

### Meduim graphs

|Graph Name   |Correct Max Clique|Graph Complexity|Found Max Clique|Is Clique|Consumed Time(seconds)|
|-------------|------------------|----------------|----------------|---------|-------------|
|brock200_2 |12                |M               |12               |True     |362.093        |
|brock200_3 |15                 |M                 |15               |True     |809.074     |
|brock200_4      |17               |M                |17              |True     |**2064.928**        |
|C125.9    |34               |M                 |34              |True     |**22.195**     |
|gen200_p0.9_44  |44                |M                  |44              |True     |6309.65      |
|gen200_p0.9_45  |55                |M                  |55              |True     |181.005      |
