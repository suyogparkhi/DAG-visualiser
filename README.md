# DAG Register Allocation

This project implements a Directed Acyclic Graph (DAG) visualization and register allocation using the labeling algorithm. The program constructs a DAG, visualizes it, and calculates the minimum number of registers required using live range analysis.

## Background

In compiler design, register allocation is an important optimization step. This project uses a graph-based approach where nodes represent values and edges represent dependencies. The register allocation algorithm assigns a minimum number of registers to the nodes, ensuring that values with overlapping live ranges don't share registers.

## Features

- Creation of custom DAGs or random DAG generation
- Visualization of the DAG structure
- Computation of node levels in the DAG
- Calculation of live ranges for each node
- Register allocation using the labeling algorithm
- Determination of the minimum number of registers required
- Web interface for interactive DAG creation and visualization

## Requirements

- Python 3.6+
- NetworkX 3.1+
- Matplotlib 3.7.1+
- Flask 2.3.3+
- NumPy<2.0 (compatibility requirement)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command-line Interface

Run the Python script for command-line usage:

```bash
python dag_register_allocation.py  # For random DAG generation
python example_dag.py              # For the predefined example
```

### Web Interface

Run the Flask web application:

```bash
python app.py
```

Then, open your browser and navigate to: http://127.0.0.1:5000/

The web interface allows you to:
1. Generate random DAGs with configurable parameters
2. Create custom DAGs by adding nodes and edges interactively
3. Run the predefined example DAG
4. Visualize the DAG and register allocation results
5. View detailed information about node levels, live ranges, and register assignments

## Output

The program will display:
- A visualization of the DAG
- Node levels (longest path from any root)
- Live ranges for each node (start and end levels)
- Register allocation for each node
- The minimum number of registers required

## How It Works

1. **DAG Creation**: Either generates a random DAG or allows manual creation
2. **Node Level Computation**: Determines the level (depth) of each node in the graph
3. **Live Range Analysis**: Calculates when each value is "live" (needed)
4. **Register Allocation**: Uses the labeling algorithm to assign registers minimizing overlap
5. **Visualization**: Shows the DAG structure with register assignments 