import logging


class Node:
    def __init__(self, name):
        self.name = name
        self.edges = []

    def add_edge(self, dependency):
        self.edges.append(dependency)

    def __repr__(self):
        return self.name


class Resolver:

    def __init__(self, graph):
        self.graph = graph

    def resolve_dependency(self, node, resolved, unresolved):

        if node in resolved:
            return

        unresolved.append(node)

        for edge in node.edges:
            if edge not in resolved:

                if edge in unresolved:
                    raise Exception('Circular reference detected: %s -&gt; %s'.format(node.name, edge.name))

                self.resolve_dependency(edge, resolved, unresolved)

        resolved.append(node)
        unresolved.remove(node)

    def resolve_dependencies(self):

        resolved = []
        for node in self.graph:
            self.resolve_dependency(node, resolved, [])

        logging.debug("Resolved dependency order {:s}".format(str(resolved)))
        return resolved
