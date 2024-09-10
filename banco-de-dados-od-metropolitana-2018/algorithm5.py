import pandas as pd
import folium
from folium import plugins
import json

from tqdm import tqdm

class MetroNetworkDesign:
    def __init__(self, nodes_df, edges_df, coverage_threshold, target_zones):
        # Prune nodes with low path coverage
        self.nodes = nodes_df[(nodes_df['path_coverage'] > coverage_threshold) | (nodes_df['zone'].isin(target_zones))]
        self.edges = edges_df[edges_df['source'].isin(self.nodes['id']) & edges_df['target'].isin(self.nodes['id'])]
        self.target_zones = target_zones
        self.solutions = []  # List to store solutions

    def compute_total_coverage(self, path):
        # Calculate the total path coverage for a given path
        total_coverage = sum(self.nodes.loc[self.nodes['id'].isin(path), 'path_coverage'])
        return total_coverage

    def find_best_path(self, start_node, end_node):
    # Greedy heuristic to find a path with high coverage
        current_node = start_node
        visited = [current_node]
        
        while current_node != end_node:
            # Get the neighbors of the current node
            neighbors = self.edges[self.edges['source'] == current_node]['target']
            if neighbors.empty:
                break
            
            # Filter out neighbors that are isolated and not the end node
            valid_neighbors = [
                neighbor for neighbor in neighbors
                if (neighbor in self.edges['source'].values) or (neighbor == end_node)
            ]
            
            if not valid_neighbors:
                break
            
            # Choose the neighbor with the highest path coverage that hasn't been visited
            best_neighbor = None
            max_coverage = -1
            for neighbor in valid_neighbors:
                if neighbor not in visited:
                    coverage = self.nodes.loc[self.nodes['id'] == neighbor, 'path_coverage'].values[0]
                    if coverage > max_coverage:
                        max_coverage = coverage
                        best_neighbor = neighbor
            
            if best_neighbor is None:
                break
            
            visited.append(best_neighbor)
            current_node = best_neighbor

        return visited, self.compute_total_coverage(visited)


    def algorithm_5(self):
        solutions = []

        # Define origin and destination zone pairs
        zone_pairs = [
            (59, 173), (59, 52), (59, 24), (59, 215),
            (173, 24), (173, 215),
            (52, 24), (52, 215)
        ]

        total_pairs = len(zone_pairs)
        with tqdm(total=total_pairs, desc="Calculating best paths") as pbar:
            for i, (origin_zone, destination_zone) in enumerate(zone_pairs):
                origin_nodes = self.nodes[self.nodes['zone'] == origin_zone]
                destination_nodes = self.nodes[self.nodes['zone'] == destination_zone]
                if not origin_nodes.empty and not destination_nodes.empty:
                    start_node = origin_nodes.iloc[0]['id']
                    end_node = destination_nodes.iloc[0]['id']
                    best_path, max_coverage = self.find_best_path(start_node, end_node)
                    solutions.append((best_path, max_coverage))
                    pbar.update(1)

        return solutions

# Function to generate the HTML content using folium
def generate_html(nodes_df, solutions):
    print('generating html')
    # Initialize a folium map
    center_lat = nodes_df["y"].mean()
    center_lng = nodes_df["x"].mean()
    m = folium.Map(location=[center_lat, center_lng], zoom_start=13)

    # Extract nodes that are part of edges
    edge_nodes = set()
    for _, edge in edges_df.iterrows():
        edge_nodes.add(edge['source'])
        edge_nodes.add(edge['target'])

    # Filter nodes to include only those in edges
    filtered_nodes_df = nodes_df[nodes_df['id'].isin(edge_nodes)]

    # Add nodes to map
    for _, node in filtered_nodes_df.iterrows():
        folium.CircleMarker(
            location=[node["y"], node["x"]],
            radius=5,
            color='#3388ff',
            fill=True,
            fill_color='#3388ff',
            fill_opacity=0.8,
            popup=f'Node ID: {node["id"]}<br>Path Coverage: {node["path_coverage"]}'
        ).add_to(m)

    # Add edges to map
    for path, _ in solutions:
        for i in range(len(path) - 1):
            source_node = filtered_nodes_df[filtered_nodes_df["id"] == path[i]].iloc[0]
            target_node = filtered_nodes_df[filtered_nodes_df["id"] == path[i + 1]].iloc[0]
            folium.PolyLine(
                locations=[
                    [source_node["y"], source_node["x"]],
                    [target_node["y"], target_node["x"]]
                ],
                color='red'
            ).add_to(m)

    # Save the map to an HTML file
    html_file = 'metro_network_solution.html'
    m.save(html_file)
    return html_file


# Example usage
nodes_df = pd.read_csv('nodes.csv')
edges_df = pd.read_csv('edges.csv')

# Define a coverage threshold for pruning and target zones
coverage_threshold = 0.01  # Adjust this threshold based on your dataset
target_zones = [173, 53, 24, 215, 59]  # Corresponding to T1, T2, T3, T4, T5

# Run the algorithm with pruning and a heuristic method
metro_network = MetroNetworkDesign(nodes_df, edges_df, coverage_threshold, target_zones)
solutions = metro_network.algorithm_5()

# Generate the HTML
html_file = generate_html(nodes_df, solutions)

print(f"HTML file created: {html_file}")
