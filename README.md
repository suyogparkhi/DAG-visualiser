# Register Allocation with DAG Visualization

This Flask application provides a web-based GUI for visualizing register allocation using Directed Acyclic Graphs (DAGs), implementing the Sethi-Ullman labeling algorithm. The app allows users to input arithmetic expressions, visualizes the resulting DAG, and demonstrates the register allocation process.

## Features

- Parse arithmetic expressions into DAG representation
- Calculate minimum register requirements using the Sethi-Ullman algorithm
- Visualize the DAG with labeled nodes
- Generate step-by-step register allocation instructions
- Interactive web interface

## Installation

1. Clone this repository or download the source code

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Enter an arithmetic expression (e.g., `a + b * (c + d) - e`)

4. Click "Analyze" to see the DAG visualization and register allocation details

## How It Works

### DAG Construction
The application parses arithmetic expressions into a DAG where:
- Leaf nodes represent variables or constants
- Internal nodes represent operations
- Edges represent data dependencies

### Register Allocation Algorithm
The Sethi-Ullman algorithm assigns "labels" to nodes based on these rules:
- Leaf nodes get label 1 (they need 1 register)
- For internal nodes with children of different labels, the node's label is max(left.label, right.label)
- If both children have the same label k, the node's label is k+1

### Code Generation
The application generates step-by-step instructions for register allocation:
- Determines evaluation order (evaluating the more complex subtree first)
- Tracks register usage across the evaluation
- Outputs a sequence of instructions that minimizes register usage

## Example

For the expression `a + b * (c + d) - e`:

1. The algorithm constructs a DAG with operations (+, *, -) and variables (a, b, c, d, e)
2. Assigns labels to determine minimum register requirements
3. Generates allocation steps showing which registers to use
4. The root label indicates the minimum number of registers needed (2 in this case)

## Extending the Application

- Add support for more complex expressions
- Implement register spilling for cases where not enough registers are available
- Add visualization of the actual register allocation process
- Support different register allocation algorithms for comparison