import os
import re
import json
import networkx as nx
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class DAGNode:
    """Represents a node in the DAG for register allocation."""
    def __init__(self, id, value, node_type="operation"):
        self.id = id
        self.value = value  # Variable name or operation
        self.node_type = node_type  # "variable" or "operation"
        self.children = []
        self.label = None  # Register requirement
    
    def add_child(self, child):
        """Add a child node to this node."""
        self.children.append(child)
    
    def to_dict(self):
        """Convert the node to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "value": self.value,
            "type": self.node_type,
            "label": self.label,
            "children": [child.id for child in self.children]
        }

class RegisterAllocator:
    """Handles register allocation using the DAG-based labeling algorithm."""
    def __init__(self):
        self.nodes = {}
        self.root = None
        self.next_id = 0
    
    def reset(self):
        """Reset the allocator state."""
        self.nodes = {}
        self.root = None
        self.next_id = 0
    
    def get_next_id(self):
        """Generate a unique ID for a new node."""
        new_id = self.next_id
        self.next_id += 1
        return new_id
    
    def create_node(self, value, node_type="operation"):
        """Create a new node and add it to the DAG."""
        node_id = self.get_next_id()
        node = DAGNode(node_id, value, node_type)
        self.nodes[node_id] = node
        return node
    
    def parse_expression(self, expression):
        """Parse an arithmetic expression and build the DAG."""
        self.reset()
        # Remove all whitespace
        expression = re.sub(r'\s+', '', expression)
        self.root = self._parse_expression(expression)
        return self.root
    
    def _parse_expression(self, expr):
        """Recursive helper to parse expressions."""
        # Look for addition/subtraction at the top level
        parenthesis_level = 0
        for i in range(len(expr) - 1, -1, -1):  # Scan right to left for proper associativity
            if expr[i] == ')':
                parenthesis_level += 1
            elif expr[i] == '(':
                parenthesis_level -= 1
            elif parenthesis_level == 0 and expr[i] in ['+', '-']:
                # Split at this operator
                left_expr = expr[:i]
                right_expr = expr[i+1:]
                
                op_node = self.create_node(expr[i])
                left_node = self._parse_expression(left_expr)
                right_node = self._parse_expression(right_expr)
                
                op_node.add_child(left_node)
                op_node.add_child(right_node)
                return op_node
        
        # No addition/subtraction found, look for multiplication/division
        parenthesis_level = 0
        for i in range(len(expr) - 1, -1, -1):  # Scan right to left
            if expr[i] == ')':
                parenthesis_level += 1
            elif expr[i] == '(':
                parenthesis_level -= 1
            elif parenthesis_level == 0 and expr[i] in ['*', '/']:
                # Split at this operator
                left_expr = expr[:i]
                right_expr = expr[i+1:]
                
                op_node = self.create_node(expr[i])
                left_node = self._parse_expression(left_expr)
                right_node = self._parse_expression(right_expr)
                
                op_node.add_child(left_node)
                op_node.add_child(right_node)
                return op_node
        
        # No operators found, check for parentheses
        if expr.startswith('(') and expr.endswith(')'):
            return self._parse_expression(expr[1:-1])
        
        # Must be a variable or constant
        var_node = self.create_node(expr, "variable")
        return var_node
    
    def assign_labels(self):
        """Assign register requirement labels to all nodes in the DAG."""
        if self.root:
            self._assign_label(self.root)
            return self.root.label
        return None
    
    def _assign_label(self, node):
        """Recursive helper to assign labels."""
        # Leaf node (variable)
        if node.node_type == "variable":
            node.label = 1
            return 1
        
        # If node has children, process them first
        if len(node.children) == 2:
            left_child = node.children[0]
            right_child = node.children[1]
            
            left_label = self._assign_label(left_child)
            right_label = self._assign_label(right_child)
            
            # Apply the Sethi-Ullman labeling rules
            if left_label == right_label:
                node.label = left_label + 1
            else:
                node.label = max(left_label, right_label)
                
            return node.label
        elif len(node.children) == 1:
            # Unary operation
            child_label = self._assign_label(node.children[0])
            node.label = child_label
            return node.label
        
        # Default case
        node.label = 1
        return 1
    
    def get_dag_as_dict(self):
        """Convert the DAG to a dictionary for visualization."""
        if not self.nodes:
            return {}
        
        nodes_data = []
        edges_data = []
        
        for node_id, node in self.nodes.items():
            node_data = {
                "id": node_id,
                "label": f"{node.value}\nLabel: {node.label}",
                "group": "variable" if node.node_type == "variable" else "operation"
            }
            nodes_data.append(node_data)
            
            for child in node.children:
                edge_data = {
                    "from": node_id,
                    "to": child.id,
                    "arrows": "to"
                }
                edges_data.append(edge_data)
        
        return {
            "nodes": nodes_data,
            "edges": edges_data
        }

    def get_allocation_steps(self):
        """Generate step-by-step register allocation instructions."""
        if not self.root:
            return []
            
        steps = []
        self._generate_allocation_steps(self.root, steps)
        return steps
    
    def _generate_allocation_steps(self, node, steps, register_map=None):
        """Generate register allocation steps for evaluation."""
        if register_map is None:
            register_map = {}
            
        # Leaf node (variable)
        if node.node_type == "variable":
            reg = f"R{len(register_map) + 1}"
            register_map[node.id] = reg
            steps.append(f"Load {node.value} into {reg}")
            return reg
            
        # Process binary operation
        if len(node.children) == 2:
            left_child = node.children[0]
            right_child = node.children[1]
            
            # Decide evaluation order based on labels
            if left_child.label < right_child.label:
                # Evaluate right subtree first (it needs more registers)
                right_reg = self._generate_allocation_steps(right_child, steps, register_map)
                left_reg = self._generate_allocation_steps(left_child, steps, register_map)
            else:
                # Evaluate left subtree first
                left_reg = self._generate_allocation_steps(left_child, steps, register_map)
                right_reg = self._generate_allocation_steps(right_child, steps, register_map)
            
            # Perform operation
            steps.append(f"{left_reg} {node.value} {right_reg} → {left_reg}")
            
            # Free the right register if it's no longer needed
            if right_reg in register_map.values():
                for k, v in list(register_map.items()):
                    if v == right_reg:
                        del register_map[k]
                        
            register_map[node.id] = left_reg
            return left_reg
            
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    expression = data.get('expression', '')
    
    allocator = RegisterAllocator()
    try:
        allocator.parse_expression(expression)
        allocator.assign_labels()
        
        return jsonify({
            'success': True,
            'dag': allocator.get_dag_as_dict(),
            'steps': allocator.get_allocation_steps(),
            'min_registers': allocator.root.label if allocator.root else 0
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Create the templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create the static directory if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Create the index.html template
with open('templates/index.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register Allocation with DAG</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <style>
        #dag-container {
            width: 100%;
            height: 500px;
            border: 1px solid #ccc;
            margin-top: 20px;
        }
        .variable-node {
            background-color: #a8d5ba;
        }
        .operation-node {
            background-color: #f9d5e5;
        }
        .step {
            padding: 5px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1 class="text-center mb-4">Register Allocation using DAG</h1>
        
        <div class="row">
            <div class="col-md-8 offset-md-2">
                <div class="card">
                    <div class="card-header">
                        <h5>Input Expression</h5>
                    </div>
                    <div class="card-body">
                        <form id="expression-form">
                            <div class="mb-3">
                                <label for="expression" class="form-label">Enter an arithmetic expression:</label>
                                <input type="text" class="form-control" id="expression" placeholder="e.g., a + b * (c + d) - e">
                            </div>
                            <button type="submit" class="btn btn-primary">Analyze</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5>DAG Visualization</h5>
                    </div>
                    <div class="card-body">
                        <div id="dag-container"></div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Register Allocation</h5>
                    </div>
                    <div class="card-body">
                        <div id="min-registers"></div>
                        <hr>
                        <h6>Allocation Steps:</h6>
                        <div id="allocation-steps"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-8 offset-md-2">
                <div class="card">
                    <div class="card-header">
                        <h5>Algorithm Explanation</h5>
                    </div>
                    <div class="card-body">
                        <h6>Sethi-Ullman Register Allocation Algorithm:</h6>
                        <ol>
                            <li>Represent the expression as a DAG where nodes are operations and leaves are variables/constants.</li>
                            <li>Assign a "label" to each node that represents the minimum number of registers needed for that subtree.</li>
                            <li>For leaf nodes (variables), the label is 1.</li>
                            <li>For internal nodes with two children of labels L₁ and L₂:
                                <ul>
                                    <li>If L₁ ≠ L₂, the label is max(L₁, L₂)</li>
                                    <li>If L₁ = L₂, the label is L₁ + 1</li>
                                </ul>
                            </li>
                            <li>The label of the root node indicates the minimum number of registers needed for the entire expression.</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('expression-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const expression = document.getElementById('expression').value.trim();
            
            if (expression) {
                fetch('/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ expression: expression })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        visualizeDAG(data.dag);
                        displayAllocationInfo(data.min_registers, data.steps);
                    } else {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while processing the expression.');
                });
            }
        });
        
        function visualizeDAG(dagData) {
            const container = document.getElementById('dag-container');
            
            // Node display options
            const nodes = new vis.DataSet(dagData.nodes.map(node => ({
                id: node.id,
                label: node.label,
                color: {
                    background: node.group === 'variable' ? '#a8d5ba' : '#f9d5e5',
                    border: '#2c3e50'
                },
                font: { size: 14 }
            })));
            
            // Edge display options
            const edges = new vis.DataSet(dagData.edges.map(edge => ({
                from: edge.from,
                to: edge.to,
                arrows: 'to',
                width: 2,
                color: { color: '#2c3e50' }
            })));
            
            // Network options
            const options = {
                layout: {
                    hierarchical: {
                        direction: 'UD',
                        sortMethod: 'directed',
                        levelSeparation: 100
                    }
                },
                physics: false,
                interaction: {
                    dragNodes: true,
                    dragView: true,
                    zoomView: true
                }
            };
            
            // Create the network
            new vis.Network(container, { nodes, edges }, options);
        }
        
        function displayAllocationInfo(minRegisters, steps) {
            // Display minimum registers
            const minRegistersDiv = document.getElementById('min-registers');
            minRegistersDiv.innerHTML = `<p><strong>Minimum registers required:</strong> ${minRegisters}</p>`;
            
            // Display allocation steps
            const stepsDiv = document.getElementById('allocation-steps');
            stepsDiv.innerHTML = '';
            steps.forEach((step, index) => {
                const stepElement = document.createElement('div');
                stepElement.className = 'step';
                stepElement.innerHTML = `<strong>Step ${index + 1}:</strong> ${step}`;
                stepsDiv.appendChild(stepElement);
            });
        }
    </script>
</body>
</html>''')

if __name__ == '__main__':
    app.run(debug=True)