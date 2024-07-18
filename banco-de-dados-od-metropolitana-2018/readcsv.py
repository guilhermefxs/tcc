import pandas as pd
import io

# Path to the CSV file
csv_path = 'grid.csv'

# Read the entire CSV file into a DataFrame
with open(csv_path, 'r') as f:
    content = f.read()

# Split the content by sections
sections = content.split('\n# ')

# Parse the points section
points_section = sections[0].split('\n', 1)[1]
points_df = pd.read_csv(io.StringIO(points_section))

# Parse the edges section
edges_section = sections[1].split('\n', 1)[1]
edges_df = pd.read_csv(io.StringIO(edges_section))

zone_counts = points_df['zone'].value_counts()

# Update the path_coverage for each point
points_df['path_coverage'] = points_df.apply(
    lambda row: row['path_coverage'] / zone_counts[row['zone']], axis=1
)

# Save the updated points and edges back to the CSV file
output_csv = 'grid_updated.csv'
with open(output_csv, 'w') as f:
    f.write('# Points\n')
    points_df.to_csv(f, index=False)
    f.write('\n# Edges\n')
    edges_df.to_csv(f, index=False)

print(f"Updated CSV file created at: {output_csv}")


# Display the data
print("Points DataFrame:")
print(points_df.head())

print("\nEdges DataFrame:")
print(edges_df.head())

# Now you can work with the DataFrames
