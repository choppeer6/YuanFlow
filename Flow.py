from Edge import Edge


class Flow:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self,node):
        self.nodes[node.id] = node

    def add_edge(self,source,target):
        self.edges.append(Edge(source,target))