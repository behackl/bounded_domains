import matplotlib

from bounded_domains import Node, PolygonalDomain, WeightedGraph, rectangle_domain_data

matplotlib.use("agg")  # filewriting-only backend

# domain = PolygonalDomain.from_files(
#     Path("tests") / "resources/3x3_elements_2d.txt",
#     Path("tests") / "resources/3x3_coords_2d.txt",
# )

domain = PolygonalDomain(*rectangle_domain_data(5, 15))

# domain = PolygonalDomain(*rectangle_domain_data(42, 42))

# domain = PolygonalDomain.from_files(
#     Path("tests") / "resources/117x34_elements_2d.txt",
#     Path("tests") / "resources/117x34_coords_2d.txt",
# )

print(f"{domain} and corresponding mappings created.")

node_1 = Node(0.5, 0.5)
closest_element_1 = domain.closest_element(node_1)
distance_1 = domain.distance_to_element(node_1, closest_element_1.id)
print(
    f"A closest element to {node_1} is {closest_element_1} "
    f"with a distance of {distance_1}."
)

node_2 = Node(0.5, -1)
closest_element_2 = domain.closest_element(node_2)
distance_2 = domain.distance_to_element(node_2, closest_element_2.id)
print(
    f"A closest element to {node_2} is {closest_element_2} "
    f"with a distance of {distance_2}."
)

graph = WeightedGraph(domain)
print(f"{graph} initialized with data from {domain}.")

graph._adjacency_matrix.plot("demo_plot_matrix.png")
print("Adjacency matrix plotted.")
graph.plot("demo_plot_graph.png", figsize=(20, 20))
print("Graph plotted.")
