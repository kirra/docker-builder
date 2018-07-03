import logging
from typing import List

NodeList = List['Node']


class ResolverException(Exception):
    pass


class Node:
    def __init__(self, name: str):
        self.name = name
        self.edges = []

    def add_edge(self, node: 'Node') -> None:
        """
        Adds an edge to the node.
        :param node: The node to create the edge with.
        :return: None.
        """

        self.edges.append(node)

    def __repr__(self):
        return self.name


class Resolver:
    def __init__(self, nodes: NodeList):
        self.nodes = nodes

    def resolve_dependency(self, node: Node, resolved: NodeList, unresolved: NodeList) -> None:
        """
        Resolves the dependencies for a single node.
        :param node: The node to resolve the dependencies for.
        :param resolved: A list of resolved dependencies.
        :param unresolved: A list of unresolved dependencies.
        :return: None.
        """

        if node in resolved:
            return

        unresolved.append(node)

        for edge in node.edges:
            if edge not in resolved:

                if edge in unresolved:
                    raise ResolverException(
                        "Circular dependency detected: %s -> %s".format(node.name, edge.name))

                self.resolve_dependency(edge, resolved, unresolved)

        resolved.append(node)
        unresolved.remove(node)

    def resolve_dependencies(self) -> NodeList:
        """
        Resolves the dependencies for the graph.
        :return: NodeList A list of resolved, ordered dependencies.
        """

        resolved = []
        for node in self.nodes:
            self.resolve_dependency(node, resolved, [])

        logging.debug("Resolved dependency order {:s}".format(str(resolved)))

        return resolved


class Graph:
    def __init__(self):
        self.local_nodes = {}
        self.remote_nodes = {}
        self.nodes = {}

    def add_local(self, node: Node) -> None:
        """
        Adds a node to the local nodes.
        :param node: The node to add.
        :return: None.
        """

        self.nodes[node.name] = node
        self.local_nodes[node.name] = node

    def add_remote(self, node: Node) -> None:
        """
        Adds a node to the remote nodes.
        :param node: The node to add.
        :return: None.
        """

        self.nodes[node.name] = node
        self.remote_nodes[node.name] = node

