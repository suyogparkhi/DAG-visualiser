import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import defaultdict

class DAGRegisterAllocation:
    def __init__(self):
        self.dag = nx.DiGraph()
        self.node_labels = {}
        self.live_ranges = {}
        self.registers = {}
        
    def add_node(self, node_id, value=None):
        """Add a node to the DAG with an optional value."""
        self.dag.add_node(node_id, value=value)
        
    def add_edge(self, from_node, to_node):
        """Add a directed edge from one node to another."""
        if from_node not in self.dag.nodes:
            self.add_node(from_node)
        if to_node not in self.dag.nodes:
            self.add_node(to_node)
        
        self.dag.add_edge(from_node, to_node)
        
    def generate_random_dag(self, num_nodes, edge_probability=0.3):
        """Generate a random DAG with the specified number of nodes."""
        # Clear existing graph
        self.dag = nx.DiGraph()
        
        # Add nodes
        for i in range(num_nodes):
            self.add_node(i, f"var_{i}")
        
        # Add edges (ensuring acyclicity by only connecting to higher-numbered nodes)
        for i in range(num_nodes):
            for j in range(i+1, num_nodes):
                if random.random() < edge_probability:
                    self.add_edge(i, j)
    
    def visualize(self, with_labels=True):
        """Visualize the DAG with optional register allocation labels."""
        plt.figure(figsize=(12, 8))
        
        # Create position layout for nodes
        pos = nx.spring_layout(self.dag, seed=42)
        
        # Draw nodes and edges
        nx.draw_networkx_nodes(self.dag, pos, node_size=500, node_color="lightblue")
        nx.draw_networkx_edges(self.dag, pos, arrowsize=20, width=1.5)
        
        # Draw node labels
        node_labels = {}
        for node in self.dag.nodes:
            if with_labels and node in self.registers:
                node_labels[node] = f"{node}\nR{self.registers[node]}"
            else:
                node_labels[node] = str(node)
        
        nx.draw_networkx_labels(self.dag, pos, labels=node_labels, font_size=10)
        
        # Add title
        plt.title("Directed Acyclic Graph with Register Allocation" if with_labels else "Directed Acyclic Graph")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig("dag_visualization.png")
        plt.show()
    
    def compute_node_levels(self):
        """Compute the level of each node in the DAG (longest path from any root)."""
        # Initialize all nodes with level 0
        levels = {node: 0 for node in self.dag.nodes}
        
        # Process nodes in topological order
        for node in nx.topological_sort(self.dag):
            # For each predecessor, update level if necessary
            for pred in self.dag.predecessors(node):
                levels[node] = max(levels[node], levels[pred] + 1)
                
        self.node_labels = levels
        return levels
    
    def compute_live_ranges(self):
        """Compute live ranges for each node."""
        levels = self.compute_node_levels()
        
        # For each node, find the highest level among its successors
        live_ranges = {}
        for node in self.dag.nodes:
            start = levels[node]
            end = start  # Default if no successors
            
            for succ in nx.descendants(self.dag, node):
                if levels[succ] > end:
                    end = levels[succ]
            
            live_ranges[node] = (start, end)
            
        self.live_ranges = live_ranges
        return live_ranges
    
    def allocate_registers(self):
        """Allocate registers using the labeling algorithm."""
        live_ranges = self.compute_live_ranges()
        
        # Sort nodes by increasing order of start time
        sorted_nodes = sorted(live_ranges.keys(), key=lambda n: live_ranges[n][0])
        
        # Keep track of which registers are free at each point
        registers_in_use = {}
        max_register = -1
        
        for node in sorted_nodes:
            start, end = live_ranges[node]
            
            # Find the first available register
            available_registers = set(range(len(self.dag.nodes)))
            for other_node, reg in registers_in_use.items():
                other_start, other_end = live_ranges[other_node]
                # If the live ranges overlap, this register is not available
                if not (end < other_start or start > other_end):
                    available_registers.discard(reg)
            
            if available_registers:
                reg = min(available_registers)
            else:
                # Need a new register
                reg = max_register + 1
                max_register = reg
            
            registers_in_use[node] = reg
            self.registers[node] = reg
        
        return self.registers, max_register + 1
    
    def print_results(self):
        """Print the results of register allocation."""
        print("\nNode Levels:")
        for node, level in sorted(self.node_labels.items()):
            print(f"Node {node}: Level {level}")
        
        print("\nLive Ranges:")
        for node, (start, end) in sorted(self.live_ranges.items()):
            print(f"Node {node}: Start at level {start}, End at level {end}")
        
        print("\nRegister Allocation:")
        for node, reg in sorted(self.registers.items()):
            print(f"Node {node} -> Register R{reg}")
        
        _, min_registers = self.allocate_registers()
        print(f"\nMinimum number of registers required: {min_registers}")


# Example usage
if __name__ == "__main__":
    # Create a DAG instance
    dag = DAGRegisterAllocation()
    
    # Option 1: Generate a random DAG
    dag.generate_random_dag(10, edge_probability=0.3)
    
    # Option 2: Create a specific DAG (uncomment and modify as needed)
    # dag = DAGRegisterAllocation()
    # dag.add_node(0, "a")
    # dag.add_node(1, "b")
    # dag.add_node(2, "c")
    # dag.add_node(3, "d")
    # dag.add_node(4, "e")
    # dag.add_edge(0, 1)
    # dag.add_edge(0, 2)
    # dag.add_edge(1, 3)
    # dag.add_edge(2, 3)
    # dag.add_edge(2, 4)
    
    # Visualize the DAG (before register allocation)
    dag.visualize(with_labels=False)
    
    # Allocate registers
    registers, min_registers = dag.allocate_registers()
    
    # Print results
    dag.print_results()
    
    # Visualize the DAG with register allocation
    dag.visualize(with_labels=True)
    
    print(f"\nThe visualization has been saved as 'dag_visualization.png'") 