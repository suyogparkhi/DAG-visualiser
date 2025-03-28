from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import os
import json
import base64
from io import BytesIO
from dag_register_allocation import DAGRegisterAllocation

app = Flask(__name__)
app.secret_key = 'dag_register_allocation_secret_key'

# Ensure static folder exists
os.makedirs('static', exist_ok=True)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate_random', methods=['POST'])
def generate_random():
    """Generate a random DAG based on user parameters"""
    num_nodes = int(request.form.get('num_nodes', 10))
    edge_probability = float(request.form.get('edge_probability', 0.3))
    
    # Create DAG
    dag = DAGRegisterAllocation()
    dag.generate_random_dag(num_nodes, edge_probability)
    
    # Save DAG to session
    save_dag_to_file(dag)
    
    # Generate visualization
    dag_img = get_dag_image(dag, with_labels=False)
    
    # Allocate registers
    registers, min_registers = dag.allocate_registers()
    
    # Get visualization with registers
    dag_with_registers_img = get_dag_image(dag, with_labels=True)
    
    # Get node data
    node_levels = dag.node_labels
    live_ranges = dag.live_ranges
    register_allocation = dag.registers
    
    return render_template(
        'result.html',
        dag_img=dag_img,
        dag_with_registers_img=dag_with_registers_img,
        min_registers=min_registers,
        node_levels=node_levels,
        live_ranges=live_ranges,
        register_allocation=register_allocation
    )

@app.route('/create_custom', methods=['GET', 'POST'])
def create_custom():
    """Create a custom DAG"""
    if request.method == 'GET':
        return render_template('create_custom.html')
    
    # Process form data to create a DAG
    dag = DAGRegisterAllocation()
    
    # Get node data
    node_data = json.loads(request.form.get('node_data', '[]'))
    
    # Get edge data
    edge_data = json.loads(request.form.get('edge_data', '[]'))
    
    # Add nodes
    for node in node_data:
        node_id = int(node['id'])
        value = node['value']
        dag.add_node(node_id, value)
    
    # Add edges
    for edge in edge_data:
        from_node = int(edge['from'])
        to_node = int(edge['to'])
        dag.add_edge(from_node, to_node)
    
    # Save DAG to session
    save_dag_to_file(dag)
    
    # Generate visualization
    dag_img = get_dag_image(dag, with_labels=False)
    
    # Allocate registers
    registers, min_registers = dag.allocate_registers()
    
    # Get visualization with registers
    dag_with_registers_img = get_dag_image(dag, with_labels=True)
    
    # Get node data
    node_levels = dag.node_labels
    live_ranges = dag.live_ranges
    register_allocation = dag.registers
    
    return render_template(
        'result.html',
        dag_img=dag_img,
        dag_with_registers_img=dag_with_registers_img,
        min_registers=min_registers,
        node_levels=node_levels,
        live_ranges=live_ranges,
        register_allocation=register_allocation
    )

@app.route('/example_dag')
def example_dag():
    """Run the example DAG from example_dag.py"""
    # Create a DAG instance with a specific structure
    dag = DAGRegisterAllocation()

    # Create a DAG that represents a code fragment
    # Add nodes (variables)
    dag.add_node(0, "a")  # a = 5
    dag.add_node(1, "b")  # b = 7
    dag.add_node(2, "c")  # c = a + b
    dag.add_node(3, "d")  # d = a * c
    dag.add_node(4, "e")  # e = b + d
    dag.add_node(5, "f")  # f = c - e

    # Add edges (dependencies)
    dag.add_edge(0, 2)  # a is used to compute c
    dag.add_edge(1, 2)  # b is used to compute c
    dag.add_edge(0, 3)  # a is used to compute d
    dag.add_edge(2, 3)  # c is used to compute d
    dag.add_edge(1, 4)  # b is used to compute e
    dag.add_edge(3, 4)  # d is used to compute e
    dag.add_edge(2, 5)  # c is used to compute f
    dag.add_edge(4, 5)  # e is used to compute f
    
    # Save DAG to session
    save_dag_to_file(dag)
    
    # Generate visualization
    dag_img = get_dag_image(dag, with_labels=False)
    
    # Allocate registers
    registers, min_registers = dag.allocate_registers()
    
    # Get visualization with registers
    dag_with_registers_img = get_dag_image(dag, with_labels=True)
    
    # Get node data
    node_levels = dag.node_labels
    live_ranges = dag.live_ranges
    register_allocation = dag.registers
    
    return render_template(
        'result.html',
        dag_img=dag_img,
        dag_with_registers_img=dag_with_registers_img,
        min_registers=min_registers,
        node_levels=node_levels,
        live_ranges=live_ranges,
        register_allocation=register_allocation,
        example=True,
        code=[
            "a = 5",
            "b = 7",
            "c = a + b",
            "d = a * c",
            "e = b + d",
            "f = c - e"
        ]
    )

def get_dag_image(dag, with_labels=True):
    """Generate a base64 encoded image of the DAG"""
    plt.figure(figsize=(10, 6))
    
    # Create position layout for nodes
    pos = nx.spring_layout(dag.dag, seed=42)
    
    # Draw nodes and edges
    nx.draw_networkx_nodes(dag.dag, pos, node_size=500, node_color="lightblue")
    nx.draw_networkx_edges(dag.dag, pos, arrowsize=20, width=1.5)
    
    # Draw node labels
    node_labels = {}
    for node in dag.dag.nodes:
        if with_labels and node in dag.registers:
            node_labels[node] = f"{node}\nR{dag.registers[node]}"
        else:
            node_labels[node] = str(node)
    
    nx.draw_networkx_labels(dag.dag, pos, labels=node_labels, font_size=10)
    
    # Add title
    plt.title("DAG with Register Allocation" if with_labels else "Directed Acyclic Graph")
    plt.axis('off')
    plt.tight_layout()
    
    # Save to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    # Convert to base64 for embedding in HTML
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def save_dag_to_file(dag):
    """Save the DAG to a static file for download"""
    plt.figure(figsize=(12, 8))
    
    # Create position layout for nodes
    pos = nx.spring_layout(dag.dag, seed=42)
    
    # Draw nodes and edges
    nx.draw_networkx_nodes(dag.dag, pos, node_size=500, node_color="lightblue")
    nx.draw_networkx_edges(dag.dag, pos, arrowsize=20, width=1.5)
    
    # Draw node labels
    node_labels = {}
    for node in dag.dag.nodes:
        if node in dag.registers:
            node_labels[node] = f"{node}\nR{dag.registers[node]}"
        else:
            node_labels[node] = str(node)
    
    nx.draw_networkx_labels(dag.dag, pos, labels=node_labels, font_size=10)
    
    # Add title
    plt.title("DAG with Register Allocation")
    plt.axis('off')
    plt.tight_layout()
    
    # Save to file
    plt.savefig("static/dag_visualization.png")
    plt.close()


if __name__ == '__main__':
    app.run(debug=True) 