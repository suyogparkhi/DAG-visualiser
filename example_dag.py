from dag_register_allocation import DAGRegisterAllocation

# Create a DAG instance with a specific structure
dag = DAGRegisterAllocation()

# Create a DAG that represents a code fragment
# For example:
# a = 5
# b = 7
# c = a + b
# d = a * c
# e = b + d
# f = c - e

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

print("Example DAG representing a code fragment:")
print("a = 5")
print("b = 7")
print("c = a + b")
print("d = a * c")
print("e = b + d")
print("f = c - e")
print("\n")

# Visualize the DAG (before register allocation)
print("Visualizing the DAG...")
dag.visualize(with_labels=False)

# Allocate registers
print("Allocating registers...")
registers, min_registers = dag.allocate_registers()

# Print results
dag.print_results()

# Visualize the DAG with register allocation
print("\nVisualizing the DAG with register allocation...")
dag.visualize(with_labels=True)

print(f"\nThe visualization has been saved as 'dag_visualization.png'")
print(f"\nMinimum number of registers required: {min_registers}") 