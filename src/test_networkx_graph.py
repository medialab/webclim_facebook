import os

import networkx as nx
import matplotlib.pyplot as plt


topic_color = {
    "covid": "salmon",
    "health": "khaki",
    "climate": "dodgerblue"
}

G = nx.Graph()

G.add_nodes_from([
    (0, {"name": "central", "topic": "covid"}),
    (1, {"name": "climate1", "topic": "climate"}),
    (2, {"name": "climate2", "topic": "climate"}),
    (3, {"name": "climate3", "topic": "climate"}),
    (4, {"name": "health1", "topic": "health"}),
    (5, {"name": "health2", "topic": "health"}),
    (6, {"name": "covid1", "topic": "covid"}),
    (7, {"name": "covid2", "topic": "covid"}),
    (8, {"name": "covid3", "topic": "covid"})
])

G.add_edges_from([
    (0, 1), 
    (0, 3),
    (1, 2), 
    (1, 3),
    (2, 3),  
    (0, 4),
    (3, 4),  
    (4, 5),
    (4, 6),
    (5, 6),
    (5, 8),
    (0, 6),
    (0, 7),
    (6, 7),
    (6, 8),
    (7, 8),
])

pos=nx.spring_layout(G)

labels = {0: 'central', 1: 'climate1'}

color = [topic_color[data["topic"]] for v, data in G.nodes(data=True)]

fig = plt.figure()

nx.draw_networkx_nodes(G, pos=pos, node_color=color)

nx.draw_networkx_edges(G, pos=pos, alpha=0.3, edge_color="white")

pos_higher = {}
for k, v in pos.items():
    pos_higher[k] = (v[0], v[1] + 0.1)

nx.draw_networkx_labels(
    G, pos=pos_higher, 
    labels=labels, font_color='white'
)

fig.set_facecolor("#00000F")
plt.axis("off")
plt.show()

# graph_path = os.path.join(".", "test_gephi.gexf")
# nx.write_gexf(G, graph_path)