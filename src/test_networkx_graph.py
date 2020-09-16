# import os

# import networkx as nx
# import matplotlib.pyplot as plt


# G = nx.Graph()

# G.add_nodes_from([
#     (0, {"name": "health", "node_number": 124}),
#     (1, {"name": "covid", "node_number": 659}),
#     (2, {"name": "climate", "node_number": 54})
# ])

# G.add_edges_from([
#     (0, 1), 
#     (0, 2),
#     (1, 2), 
#     (0, 0),
#     (1, 1),  
#     (2, 2)
# ])

# pos=nx.spring_layout(G)

# color = [topic_color[data["name"]] for v, data in G.nodes(data=True)]

# fig = plt.figure()

# nx.draw_networkx_nodes(G, pos=pos, node_color=color)

# nx.draw_networkx_edges(G, pos=pos, alpha=0.3, edge_color="white")

# # labels = {0: 'central', 1: 'climate1'}

# # pos_higher = {}
# # for k, v in pos.items():
# #     pos_higher[k] = (v[0], v[1] + 0.1)

# # nx.draw_networkx_labels(
# #     G, pos=pos_higher, 
# #     labels=labels, font_color='white'
# # )

# fig.set_facecolor("#00000F")
# plt.axis("off")
# plt.show()

# # graph_path = os.path.join(".", "test_gephi.gexf")
# # nx.write_gexf(G, graph_path)


import networkx as nx
from networkx.drawing.nx_agraph import to_agraph 

topic_color = {
    "health": "mediumseagreen",
    "covid": "salmon",
    "climate": "dodgerblue"
}

G = nx.Graph()

G.add_nodes_from([0], label='health\nX0 nodes', style='filled', fillcolor=topic_color['health'], width=2)
G.add_nodes_from([1], label='covid\nX1 nodes', style='filled', fillcolor=topic_color['covid'], width=4)
G.add_nodes_from([2], label='climate\nX2 nodes', style='filled', fillcolor=topic_color['climate'])

G.add_edge(0, 1, label='  X01 edges')
G.add_edge(0, 2, label='  X02 edges')
G.add_edge(1, 2, label='  X12 edges')
G.add_edge(0, 0, label='   X00 edges', penwidth=10)
G.add_edge(1, 1, label='   X11 edges', penwidth=2)
G.add_edge(2, 2, label='   X22 edges', penwidth=1)

G.graph['node']={'shape':'circle'}

A = to_agraph(G) 
A.layout('dot')
A.draw('figure_5.png')