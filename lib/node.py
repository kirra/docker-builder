class Node:
    def __init__(self, name):
        self.name = name
        self.edges = []

    def add_edge(self, dependency):
        self.edges.append(dependency)

